import os
import math
from typing import Optional
from icb.core.db_session import get_db
from main import website
from fastapi import Depends, Query, Form, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from modules.location_id import generate_prefixed_id
from datetime import datetime
from modules.social.models import (
    TBL_SOCIAL,
    TBL_SOCIAL_DELETED,
    TBL_SOCIAL_HISTORY,
    TBL_SOCIAL_REJECTED,
    TBL_SOCIAL_UNAUTH,
)
from modules.website.upload_utils import save_upload_with_unique_name

@website.get("/socials", tags=["Social"])
async def get_social(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_SOCIAL).filter(TBL_SOCIAL.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_SOCIAL.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    base_url = os.getenv("APP_URL", "")

    data_list = [{
        'id'       : s.id,
        'name'     : s.name,
        'icon'     : s.icon,
        "icon_link": f"{base_url}/static/images/Social/{s.icon}" if s.icon  is not None else "",
        'active'   : s.active
    } for s in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Social',
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


icon_DIR = "static/images/Social"
os.makedirs(icon_DIR, exist_ok=True)

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_SOCIAL,
        TBL_SOCIAL_UNAUTH,
        TBL_SOCIAL_HISTORY,
        TBL_SOCIAL_DELETED,
        TBL_SOCIAL_REJECTED,
    ], "MCO")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result


def save_icon(icon: UploadFile) -> str:
    return save_upload_with_unique_name(icon, icon_DIR)

@website.post("/socials", tags=["Social"], status_code=201)
async def create_social(
    name  : str  = Form(...,examples=[""]),
    icon : Optional[UploadFile] = File(None),
    active: bool                 = Form(True),
    db    : Session              = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Persist the icon (if provided)
    icon_filename: Optional[str] = None
    if icon and icon.filename:
        icon_filename = save_icon(icon)

    # 3. Insert the new record
    new_item = TBL_SOCIAL(
        id            = new_id,
        name          = name,
        icon         = icon_filename,
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
        "title"  : "Social",
        "message": "Data created successfully",
        "data"   : {
            "id"        : new_item.id,
            "name"      : new_item.name,
            "icon"     : new_item.icon,
            "icon_link": f"{base_url}/static/images/Social/{new_item.icon}" if new_item.icon else "",
            "active"    : new_item.active,
        },
        "error": {},
    }
