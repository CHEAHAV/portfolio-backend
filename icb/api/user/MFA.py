from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random
import smtplib
import string
from typing import Annotated
import uuid

from fastapi import Depends, HTTPException, Query, status
from fastapi import Request
from jose import JWTError
import jwt
from requests import Session
from icb.api.user.models import TBL_USER, TBL_USER_LOCATION_ASSIGNMENT, TBL_USER_LOGIN_TOKEN
from icb.core.crud_keycloak import CODE_TTL_MINUTES, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER  
from icb.core.db_session import get_db
from icb.core.security import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, User, create_access_token, get_current_active_user
from icb.lib.keycloak_helper import SECRET_KEY
from main import app


def _send_otp_email_local(to_email: str, code: str):
    try:
        msg            = MIMEMultipart("alternative")
        msg["Subject"] = "Your Login Verification Code"
        msg["From"]    = SMTP_USER
        msg["To"]      = to_email
        msg.attach(MIMEText(
            f"Hi,\n\nYour verification code is: {code}\n\n"
            f"This code expires in {CODE_TTL_MINUTES} minutes.\n\n"
            "If you did not request this, please ignore this email.",
            "plain", "utf-8",
        ))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:  
            server.ehlo(); server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP email: {e}")


# -- 2FA enable flow ----------------------------------------------------------

@app.post("/api/v1/users/2fa-enable")
async def request_enable_2fa(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db          : Session = Depends(get_db),
):
    row = db.query(TBL_USER).filter(TBL_USER.id == current_user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found.")
    if getattr(row, "two_factor", False):
        raise HTTPException(status_code=400, detail="2FA is already enabled.")

    code       = "".join(random.choices(string.digits, k=6))
    expires_at = datetime.utcnow() + timedelta(minutes=CODE_TTL_MINUTES)
    email      = getattr(row, "email", None) or current_user.email

    row.code       = code       
    row.expires_at = expires_at
    db.commit()

    _send_otp_email_local(email, code)
    return {"ok": True, "message": "OTP sent to your email. Please verify to enable 2FA."}


@app.put("/api/v1/users/2fa-enable/verify")
async def verify_enable_2fa(
    current_user: Annotated[User, Depends(get_current_active_user)],
    code        : str = Query(...),  # ✅ explicit Query
    db          : Session = Depends(get_db),
):
    record = db.query(TBL_USER).filter(
        TBL_USER.id         == current_user.id,
        TBL_USER.code       == code,
        TBL_USER.expires_at >  datetime.utcnow(),
    ).first()
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP code.")

    record.two_factor = True
    record.code       = None 
    record.expires_at = None
    if hasattr(record, "re_updated_at"): record.re_updated_at = datetime.now()
    if hasattr(record, "re_updated_by"): record.re_updated_by = current_user.id
    db.commit()
    return {"ok": True, "message": "2FA enabled successfully."}


# --- 2FA disable flow --------------------------------------------------------

@app.post("/api/v1/users/2fa-disable")
async def request_disable_2fa(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db          : Session = Depends(get_db),
):
    row = db.query(TBL_USER).filter(TBL_USER.id == current_user.id).first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found.")
    if not getattr(row, "two_factor", False):
        raise HTTPException(status_code=400, detail="2FA is not enabled.")

    code       = "".join(random.choices(string.digits, k=6))
    expires_at = datetime.utcnow() + timedelta(minutes=CODE_TTL_MINUTES)
    email      = getattr(row, "email", None) or current_user.email

    row.code       = code       
    row.expires_at = expires_at
    db.commit()

    _send_otp_email_local(email, code)
    return {"ok": True, "message": "OTP sent to your email. Please verify to disable 2FA."}


@app.delete("/api/v1/users/2fa-disable/verify")
async def verify_disable_2fa(
    current_user: Annotated[User, Depends(get_current_active_user)],
    code        : str = Query(...), 
    db          : Session = Depends(get_db),
):
    record = db.query(TBL_USER).filter(
        TBL_USER.id         == current_user.id,
        TBL_USER.code       == code,
        TBL_USER.expires_at >  datetime.utcnow(),
    ).first()
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP code.")

    record.two_factor = False
    record.code       = None  
    record.expires_at = None
    if hasattr(record, "re_updated_at"): record.re_updated_at = datetime.now()
    if hasattr(record, "re_updated_by"): record.re_updated_by = current_user.id
    db.commit()
    return {"ok": True, "message": "2FA disabled successfully."}


# --- 2FA login verification --------------------------------------------------

@app.post("/api/v1/users/2fa-login/verify")
async def verify_2fa_login(
    request: Request,
    token  : str = Query(..., description="Pending 2FA token from login"),
    code   : str = Query(...),  
    db     : Session = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired pending token.",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        pending = payload.get("pending_2fa")
        if not user_id or not pending:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    record = db.query(TBL_USER).filter(
        TBL_USER.id         == user_id,
        TBL_USER.code       == code,
        TBL_USER.expires_at >  datetime.utcnow(),
    ).first()
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP code.")

    record.code       = None  
    record.expires_at = None
    db.commit()

    ula_obj = db.query(TBL_USER_LOCATION_ASSIGNMENT)\
        .filter(TBL_USER_LOCATION_ASSIGNMENT.user_id    == user_id)\
        .filter(TBL_USER_LOCATION_ASSIGNMENT.is_default == True)\
        .first()
    if not ula_obj:
        raise HTTPException(status_code=401, detail="User has no location assignment.")

    dnow                 = datetime.now()
    tid                  = str(uuid.uuid4())
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token         = create_access_token(
        data={"sub": user_id, "tid": tid},
        expires_delta=access_token_expires,
    )
    client_source = request.headers.get("X-Client-Source", "")

    device = db.query(TBL_USER_LOGIN_TOKEN).filter(
        TBL_USER_LOGIN_TOKEN.user_id == user_id,
        TBL_USER_LOGIN_TOKEN.device.ilike("%mozilla%") if client_source != "mobile"
        else ~TBL_USER_LOGIN_TOKEN.device.ilike("%mozilla%")
    ).first()

    if device:
        device.expire_at = str(dnow + access_token_expires)
        device.token     = tid
        db.add(device)
    else:
        db.add(TBL_USER_LOGIN_TOKEN(**{
            "user_id"           : user_id,
            "token"             : tid,
            "device"            : request.headers.get("user-agent", ""),
            "re_created_at"     : dnow,
            "expire_at"         : str(dnow + access_token_expires),
            "company_id"        : ula_obj.accessible_company_id if ula_obj else "",
            "working_store_id"  : ula_obj.default_store_id      if ula_obj else "",
            "working_company_id": ula_obj.accessible_company_id if ula_obj else "",
            "working_branch_id" : ula_obj.default_branch_id     if ula_obj else "",
        }))
    db.commit()

    return {"access_token": access_token, "token_type": "bearer"}