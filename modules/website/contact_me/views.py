import os
import math
from typing import Optional
from icb.core.db_session import get_db
from main import website
from fastapi import Depends, Query, Form, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from modules.location_id import generate_prefixed_id
from datetime import datetime
from modules.contact_me.models import (
    TBL_CONTACT_ME,
    TBL_CONTACT_ME_DELETED,
    TBL_CONTACT_ME_HISTORY,
    TBL_CONTACT_ME_REJECTED,
    TBL_CONTACT_ME_UNAUTH,
)
from modules.website.upload_utils import media_name, media_url, upload_image_to_cloudinary

@website.get("/contacts", tags=["ContactMe"])
@website.get("/contact-mes", tags=["ContactMe"], include_in_schema=False)
async def get_ContactMe(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_CONTACT_ME).filter(TBL_CONTACT_ME.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_CONTACT_ME.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    base_url = os.getenv("APP_URL", "")

    data_list = [{
        'id'         : c.id,
        'name'       : c.name,
        'description': c.description,
        'icon'       : media_name(c.icon),
        "icon_link"  : media_url(c.icon),
        'active'     : c.active
    } for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'ContactMe',
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


icon_DIR = "static/images/ContactMe"
os.makedirs(icon_DIR, exist_ok=True)

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_CONTACT_ME,
        TBL_CONTACT_ME_UNAUTH,
        TBL_CONTACT_ME_HISTORY,
        TBL_CONTACT_ME_DELETED,
        TBL_CONTACT_ME_REJECTED,
    ], "CON")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result


def save_icon(icon: UploadFile) -> str:
    return upload_image_to_cloudinary(icon, "ContactMe")

@website.post("/contact-mes", tags=["ContactMe"], status_code=201)
async def create_contact_me(
    name        : str                  = Form(...,examples=[""]),
    description : str                  = Form(...,examples=[""]),
    icon        : Optional[UploadFile] = File(None),
    active     : bool                  = Form(True),
    db          : Session              = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Persist the icon (if provided)
    icon_filename: Optional[str] = None
    if icon and icon.filename:
        icon_filename = save_icon(icon)

    # 3. Insert the new record
    new_item = TBL_CONTACT_ME(
        id            = new_id,
        name          = name,
        description   = description,
        icon          = icon_filename,
        active        = active,
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
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    base_url = os.getenv("APP_URL", "")
    return {
        "ok"     : True,
        "status" : 201,
        "title"  : "ContactMe",
        "message": "Data created successfully",
        "data"   : {
            "id"         : new_item.id,
            "name"       : new_item.name,
            "description": new_item.description,
            "icon"       : media_name(new_item.icon),
            "icon_link"  : media_url(new_item.icon),
            "active"     : new_item.active,
        },
        "error": {},
    }


@website.put("/contacts/{id}", tags=["ContactMe"])
@website.put("/contact-mes/{id}", tags=["ContactMe"], include_in_schema=False)
async def update_contact_me(
    id         : str,
    name       : str                  = Form(..., examples=[""]),
    description: str                  = Form(..., examples=[""]),
    icon       : Optional[UploadFile] = File(None),
    active     : bool                 = Form(True),
    db         : Session              = Depends(get_db),
):
    item = db.query(TBL_CONTACT_ME).filter(TBL_CONTACT_ME.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="ContactMe not found")

    item.name = name
    item.description = description
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
        "title"  : "ContactMe",
        "message": "Data updated successfully",
        "data"   : {
            "id"         : item.id,
            "name"       : item.name,
            "description": item.description,
            "icon"       : media_name(item.icon),
            "icon_link"  : media_url(item.icon),
            "active"     : item.active,
        },
        "error": {},
    }
