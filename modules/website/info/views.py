import os
import math
from typing import Optional
from icb.core.db_session import get_db
from main import website
from fastapi import Depends, Query, Form, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from modules.location_id import generate_prefixed_id
from datetime import datetime
from modules.info.models import (
    TBL_INFO,
    TBL_INFO_DELETED,
    TBL_INFO_HISTORY,
    TBL_INFO_REJECTED,
    TBL_INFO_UNAUTH,
)
from modules.website.upload_utils import save_upload_with_unique_name

@website.get("/infos", tags=["Info"])
async def get_info(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_INFO).filter(TBL_INFO.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_INFO.name\
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
        'image'      : c.image,
        "image_link" : f"{base_url}/static/images/Info/{c.image}" if c.image  is not None else "",
        'active'     : c.active
    } for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Info',
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


IMAGE_DIR = "static/images/Info"
os.makedirs(IMAGE_DIR, exist_ok=True)

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_INFO,
        TBL_INFO_UNAUTH,
        TBL_INFO_HISTORY,
        TBL_INFO_DELETED,
        TBL_INFO_REJECTED,
    ], "MCO")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result


def save_image(image: UploadFile) -> str:
    return save_upload_with_unique_name(image, IMAGE_DIR)

@website.post("/infos", tags=["Info"], status_code=201)
async def create_info(
    name        : str                  = Form(...,examples=[""]),
    description : str                  = Form(...,examples=[""]),
    image       : Optional[UploadFile] = File(None),
    active     : bool                  = Form(True),
    db          : Session              = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Persist the image (if provided)
    image_filename: Optional[str] = None
    if image and image.filename:
        image_filename = save_image(image)

    # 3. Insert the new record
    new_item = TBL_INFO(
        id            = new_id,
        name          = name,
        description   = description,
        image         = image_filename,
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
        "title"  : "Info",
        "message": "Data created successfully",
        "data"   : {
            "id"        : new_item.id,
            "name"      : new_item.name,
            "image"     : new_item.image,
            "active"    : new_item.active,
            "image_link": f"{base_url}/static/images/Info/{new_item.image}" if new_item.image else "",
        },
        "error": {},
    }
