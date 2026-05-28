import os
import math
from typing import Annotated, Optional
from icb.core.db_session import get_db
from main import website
from fastapi import Depends, Query, Form, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from modules.location_id import generate_prefixed_id
from datetime import date, datetime
from pydantic import BeforeValidator
from modules.certification.models import (
    TBL_CERTIFICATION,
    TBL_CERTIFICATION_DELETED,
    TBL_CERTIFICATION_HISTORY,
    TBL_CERTIFICATION_REJECTED,
    TBL_CERTIFICATION_UNAUTH,
)
from modules.website.upload_utils import media_name, media_url, upload_image_to_cloudinary

@website.get("/certifications", tags=["Certification"])
async def get_certification(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_CERTIFICATION).filter(TBL_CERTIFICATION.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_CERTIFICATION.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    base_url = os.getenv("APP_URL", "")

    data_list = [{
        'id'             : c.id,
        'name'           : c.name,
        'title'          : c.title,
        'issuer'         : c.issuer,
        'date_earned'    : c.date_earned.strftime("%d, %b, %Y") if c.date_earned else "",
        'credential_id'  : c.credential_id,
        'certificate_url': c.certificate_url,
        'icon'           : media_name(c.icon),
        "icon_link"      : media_url(c.icon),
        'active'         : c.active
    } for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Certification',
        'message': 'Data retrieved successfully',
        'data'   : {
            'lists'    : data_list,
            'meta_data': {
                'total'       : total,
                'total_page'  : total_pages,
                'current_page': page,
                'size'        : size,
            }
        },
        'error': {}
    }


icon_DIR = "static/images/Certification"
os.makedirs(icon_DIR, exist_ok=True)

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_CERTIFICATION,
        TBL_CERTIFICATION_UNAUTH,
        TBL_CERTIFICATION_HISTORY,
        TBL_CERTIFICATION_DELETED,
        TBL_CERTIFICATION_REJECTED,
    ], "CER")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result


def save_icon(icon: UploadFile) -> str:
    return upload_image_to_cloudinary(icon, "Certification")

def parse_date(v: str) -> date:
    return date.fromisoformat(v)

DateForm = Annotated[date, BeforeValidator(parse_date)]

@website.post("/certifications", tags=["Certification"], status_code=201)
async def create_certification(
    name            : str                  = Form(...,examples=[""]),
    title           : str                  = Form(...,examples=[""]),
    issuer          : str                  = Form(...,examples=[""]),
    date_earned     : DateForm             = Form(..., examples=["2024-01-01"]),
    credential_id   : str                  = Form(...,examples=[""]),
    certificate_url : str                  = Form(...,examples=[""]),
    icon            : Optional[UploadFile] = File(None),
    active          : bool                 = Form(True),
    db              : Session              = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Persist the icon (if provided)
    icon_filename: Optional[str] = None
    if icon and icon.filename:
        icon_filename = save_icon(icon)

    # 3. Insert the new record
    new_item = TBL_CERTIFICATION(
        id              = new_id,
        name            = name,
        title           = title,
        issuer          = issuer,
        date_earned     = date_earned,
        credential_id   = credential_id,
        certificate_url = certificate_url,
        icon            = icon_filename,
        active          = active,
        company_id      = "SYSTEM",
        branch_id       = "HQ",
        store_id        = "",
        re_version      = 0,
        re_status       = "",
        re_created_by   = "",
        re_updated_by   = "",
        re_is_public    = False,
        flow_status     = "",
        system_date     = "",
        re_created_at   = datetime.now(),
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    base_url = os.getenv("APP_URL", "")
    return {
        "ok"     : True,
        "status" : 201,
        "title"  : "Certification",
        "message": "Data created successfully",
        "data"   : {
        "id"             : new_item.id,
        "name"           : new_item.name,
        "title"          : new_item.title,
        "issuer"         : new_item.issuer,
        "date_earned"    : new_item.date_earned.strftime("%d, %b, %Y") if new_item.date_earned else "",
        "credential_id"  : new_item.credential_id,
        "certificate_url": new_item.certificate_url,
        "icon"           : media_name(new_item.icon),
        "icon_link"      : media_url(new_item.icon),
        "active"         : new_item.active,
        },
        "error": {},
    }


@website.put("/certifications/{id}", tags=["Certification"])
async def update_certification(
    id             : str,
    name           : Optional[str]        = Form(None, examples=[""]),
    title          : Optional[str]        = Form(None, examples=[""]),
    issuer         : Optional[str]        = Form(None, examples=[""]),
    date_earned    : Optional[DateForm]   = Form(None, examples=["2024-01-01"]),
    credential_id  : Optional[str]        = Form(None, examples=[""]),
    certificate_url: Optional[str]        = Form(None, examples=[""]),
    icon           : Optional[UploadFile] = File(None),
    active         : Optional[bool]       = Form(None),
    db             : Session              = Depends(get_db),
):
    item = db.query(TBL_CERTIFICATION).filter(TBL_CERTIFICATION.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Certification not found")

    if name is not None:
        item.name = name
    if title is not None:
        item.title = title
    if issuer is not None:
        item.issuer = issuer
    if date_earned is not None:
        item.date_earned = date_earned
    if credential_id is not None:
        item.credential_id = credential_id
    if certificate_url is not None:
        item.certificate_url = certificate_url
    if active is not None:
        item.active = active
    item.re_updated_at = datetime.now()
    if icon and icon.filename:
        item.icon = save_icon(icon)

    db.commit()
    db.refresh(item)

    base_url = os.getenv("APP_URL", "")
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Certification",
        "message": "Data updated successfully",
        "data"   : {
            "id"             : item.id,
            "name"           : item.name,
            "title"          : item.title,
            "issuer"         : item.issuer,
            "date_earned"    : item.date_earned.strftime("%d, %b, %Y") if item.date_earned else "",
            "credential_id"  : item.credential_id,
            "certificate_url": item.certificate_url,
            "icon"           : media_name(item.icon),
            "icon_link"      : media_url(item.icon),
            "active"         : item.active,
        },
        "error": {},
    }
