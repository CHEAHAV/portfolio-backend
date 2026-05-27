from datetime import datetime
from email.message import EmailMessage
import os
import math
import logging
import smtplib
import ssl
from types import SimpleNamespace
from modules.message.models import (
    TBL_MESSAGE,
    TBL_MESSAGE_UNAUTH,
    TBL_MESSAGE_HISTORY,
    TBL_MESSAGE_DELETED,
    TBL_MESSAGE_REJECTED,
)
from icb.core.db_session import get_db
from main import website
from fastapi import Depends, Form, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from modules.location_id import assign_prefixed_id

logger = logging.getLogger(__name__)

SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", os.getenv("SMTP_USER", ""))
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_SENDER   = os.getenv("SMTP_SENDER", SMTP_USERNAME)
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", SMTP_USERNAME)

def is_contact_email_configured() -> bool:
    return bool(SMTP_HOST and SMTP_PORT and SMTP_USERNAME and SMTP_PASSWORD and SMTP_SENDER and CONTACT_EMAIL)


def send_contact_email(
    first_name: str,
    last_name : str,
    email     : str,
    subject   : str,
    message   : str,
):
    full_name = f"{first_name} {last_name}".strip()

    body = f"""
    Dear CHEAHAV IT Team,

    A new inquiry has been submitted through the mobile contact form. Please find the details of the submission below:

    --- CLIENT DETAILS ---
    Name:           {full_name if full_name else "Not provided"}
    Email:          {email}
    Subject:        {subject}

    --- MESSAGE ---
    {message}

    ----------------------
    Note: This is an automated notification. Please reply directly to the client using the email address provided above.
"""

    email_message = EmailMessage()
    email_message["Subject"]  = subject
    email_message["From"]     = SMTP_SENDER
    email_message["To"]       = CONTACT_EMAIL
    email_message["Reply-To"] = email
    email_message.set_content(body)

    context = ssl.create_default_context()
    if SMTP_PORT == 465:
        smtp = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=20, context=context)
    else:
        smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20)

    with smtp:
        if SMTP_PORT != 465:
            smtp.starttls(context=context)
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        smtp.send_message(email_message)
        logger.info(f"Contact email sent to {CONTACT_EMAIL} from {email}")


@website.get("/messages", tags=["Message"])
async def get_messages(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db),
):
    try:
        base_query = db.query(TBL_MESSAGE).filter(TBL_MESSAGE.active == True)

        total       = base_query.count()
        results     = (
            base_query
            .order_by(TBL_MESSAGE.id.asc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        total_pages = math.ceil(total / size) if size else 1

        data_list = [
            {
                'id'        : c.id,
                'first_name': c.first_name,
                'last_name' : c.last_name,
                'email'     : c.email,
                'subject'   : c.subject,
                'message'   : c.message,
                'active'    : c.active,
            }
            for c in results
        ]

        return {
            'ok'     : True,
            'status' : 200,
            'title'  : 'Message',
            'message': 'Data retrieved successfully',
            'data'   : {
                'lists'    : data_list,
                'meta_data': {
                    'total'       : total,
                    'total_page'  : total_pages,
                    'current_page': page,
                    'size'        : size,
                },
            },
            'error': {},
        }

    except Exception as e:
        logger.error(f"Get Message error: {e}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)

@website.post("/messages", tags=["Message"])
async def message(
    first_name      : str     = Form(..., examples=[""]),
    last_name       : str     = Form(..., examples=[""]),
    email           : str     = Form(..., examples=[""]),
    subject         : str = Form(..., examples = [""]),
    message         : str     = Form(..., examples=[""]),
    db              : Session = Depends(get_db),
):
    try:
        item = {}
        assign_prefixed_id(SimpleNamespace(item=item, db=db), [
            TBL_MESSAGE,
            TBL_MESSAGE_UNAUTH,
            TBL_MESSAGE_HISTORY,
            TBL_MESSAGE_DELETED,
            TBL_MESSAGE_REJECTED,
        ], "MES")

        record = TBL_MESSAGE(
        id            = item["id"],
        first_name    = first_name,
        last_name     = last_name,
        email         = email,
        subject       = subject,
        message       = message,
        company_id    = "SYSTEM",
        branch_id     = "HQ",
        store_id      = "",
        re_version    = 0,
        re_status     = "",
        re_created_by = "",
        re_updated_by = "",
        re_is_public  = False,
        flow_status   = "",
        system_date   = "",
        re_created_at = datetime.now(),
        )
        db.add(record)
        db.commit()

        if not is_contact_email_configured():
            logger.error(
                "Contact email is not configured. Required env: SMTP_HOST, "
                "SMTP_PORT, SMTP_USERNAME or SMTP_USER, SMTP_PASSWORD, "
                "SMTP_SENDER, CONTACT_EMAIL."
            )
            return JSONResponse({
                "ok"     : False,
                "status" : 500,
                "message": "Message saved, but email is not configured on the server",
            }, status_code=500)

        try:
            send_contact_email(
                first_name,
                last_name,
                email,
                subject,
                message,
            )
        except Exception as email_error:
            logger.error(f"Contact email send failed: {email_error}", exc_info=True)
            return JSONResponse({
                "ok"     : False,
                "status" : 502,
                "message": "Message saved, but email could not be sent",
            }, status_code=502)

        return JSONResponse({
            "ok"        : True,
            "status"    : 200,
            "message"   : "Message request submitted successfully",
            "email_sent": True,
        })

    except Exception as e:
        db.rollback()
        logger.error(f"Message post error: {e}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)


@website.put("/messages/{id}", tags=["Message"])
async def update_message(
    id        : str,
    first_name: str     = Form(..., examples=[""]),
    last_name : str     = Form(..., examples=[""]),
    email     : str     = Form(..., examples=[""]),
    subject   : str     = Form(..., examples=[""]),
    message   : str     = Form(..., examples=[""]),
    active    : bool    = Form(True),
    db        : Session = Depends(get_db),
):
    record = db.query(TBL_MESSAGE).filter(TBL_MESSAGE.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Message not found")

    record.first_name = first_name
    record.last_name = last_name
    record.email = email
    record.subject = subject
    record.message = message
    record.active = active
    record.re_updated_at = datetime.now()

    db.commit()
    db.refresh(record)

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Message",
        "message": "Data updated successfully",
        "data"   : {
            "id"        : record.id,
            "first_name": record.first_name,
            "last_name" : record.last_name,
            "email"     : record.email,
            "subject"   : record.subject,
            "message"   : record.message,
            "active"    : record.active,
        },
        "error": {},
    }
