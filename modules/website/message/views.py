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
from icb.core.db_session import get_db, SessionLocal
from main import website
from fastapi import BackgroundTasks, Depends, Query, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from modules.location_id import assign_prefixed_id

logger = logging.getLogger(__name__)

SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_SENDER   = os.getenv("SMTP_SENDER", "")
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", "")

def is_contact_email_configured() -> bool:
    return bool(SMTP_USERNAME and SMTP_PASSWORD and CONTACT_EMAIL)


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
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as smtp:
        smtp.starttls(context=context)
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        smtp.send_message(email_message)
        logger.info(f"Contact email sent to {CONTACT_EMAIL} from {email}")


def send_contact_email_safe(
    first_name: str,
    last_name : str,
    email     : str,
    subject   : str,
    message   : str,
):
    try:
        send_contact_email(
            first_name,
            last_name,
            email,
            subject,
            message,
        )
    except Exception as e:
        logger.error(f"Contact email send failed: {e}", exc_info=True)


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
    background_tasks: BackgroundTasks,
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

        email_queued = is_contact_email_configured()
        if email_queued:
            background_tasks.add_task(
                send_contact_email_safe,
                first_name,
                last_name,
                email,
                subject,
                message,
            )

        return JSONResponse({
            "ok"          : True,
            "status"      : 200,
            "message"     : "Message request submitted successfully",
            "email_queued": email_queued,
        })

    except Exception as e:
        db.rollback()
        logger.error(f"Message post error: {e}", exc_info=True)
        return JSONResponse({"error": str(e)}, status_code=500)