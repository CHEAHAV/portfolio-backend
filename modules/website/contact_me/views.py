import os
import shutil
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
        'icon'       : c.icon,
        "icon_link"  : f"{base_url}/static/images/ContactMe/{c.icon}" if c.icon  is not None else "",
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
    if not icon.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename")

    dest = os.path.join(icon_DIR, icon.filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(icon.file, f)
    return icon.filename

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
            "icon"       : new_item.icon,
            "icon_link"  : f"{base_url}/static/images/ContactMe/{new_item.icon}" if new_item.icon else "",
            "active"     : new_item.active,
        },
        "error": {},
    }
