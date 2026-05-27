import os
import math
from typing import Optional
from icb.core.db_session import get_db
from main import website
from fastapi import Depends, Query, Form, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from modules.location_id import generate_prefixed_id
from datetime import datetime
from modules.mycore.models import (
    TBL_MY_CORE,
    TBL_MY_CORE_DELETED,
    TBL_MY_CORE_HISTORY,
    TBL_MY_CORE_REJECTED,
    TBL_MY_CORE_UNAUTH,
)
from modules.website.upload_utils import media_name, media_url, upload_image_to_cloudinary

@website.get("/my-cores", tags=["MyCore"])
async def get_my_core(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db:   Session = Depends(get_db),
):
    base_query  = db.query(TBL_MY_CORE).filter(TBL_MY_CORE.active == True)
    total       = base_query.count()
    results     = (
        base_query
        .order_by(TBL_MY_CORE.name.asc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    total_pages = math.ceil(total / size) if size else 1
    base_url    = os.getenv("APP_URL", "")

    data_list = [
        {
            "id"         : m.id,
            "name"       : m.name,
            "description": m.description,
            "image"      : media_name(m.image),
            "image_link" : media_url(m.image),
            "active"     : m.active,
        }
        for m in results
    ]

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "MyCore",
        "message": "Data retrieved successfully",
        "data"   : {
            "lists"    : data_list,
            "meta_data": {
                "total"       : total,
                "total_page"  : total_pages,
                "current_page": page,
                "size"        : size,
            },
        },
        "error": {},
    }


IMAGE_DIR = "static/images/MyCore"
os.makedirs(IMAGE_DIR, exist_ok=True)

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_MY_CORE,
        TBL_MY_CORE_UNAUTH,
        TBL_MY_CORE_HISTORY,
        TBL_MY_CORE_DELETED,
        TBL_MY_CORE_REJECTED,
    ], "MCO")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result


def save_image(image: UploadFile) -> str:
    return upload_image_to_cloudinary(image, "MyCore")

@website.post("/my-cores", tags=["MyCore"], status_code=201)
async def create_my_core(
    name        : str                  = Form(...,examples=[""]),
    description : str                  = Form(...,examples=[""]),
    image       : Optional[UploadFile] = File(None),
    active      : bool                 = Form(True),
    db          : Session              = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Persist the image (if provided)
    image_filename: Optional[str] = None
    if image and image.filename:
        image_filename = save_image(image)

    # 3. Insert the new record
    new_item = TBL_MY_CORE(
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
        "title"  : "MyCore",
        "message": "Data created successfully",
        "data"   : {
            "id"        : new_item.id,
            "name"      : new_item.name,
            "image"     : media_name(new_item.image),
            "active"    : new_item.active,
            "image_link": media_url(new_item.image),
        },
        "error": {},
    }


@website.put("/my-cores/{id}", tags=["MyCore"])
async def update_my_core(
    id         : str,
    name       : str                  = Form(..., examples=[""]),
    description: str                  = Form(..., examples=[""]),
    image      : Optional[UploadFile] = File(None),
    active     : bool                 = Form(True),
    db         : Session              = Depends(get_db),
):
    item = db.query(TBL_MY_CORE).filter(TBL_MY_CORE.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="MyCore not found")

    item.name = name
    item.description = description
    item.active = active
    item.re_updated_at = datetime.now()
    if image and image.filename:
        item.image = save_image(image)

    db.commit()
    db.refresh(item)

    base_url = os.getenv("APP_URL", "")
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "MyCore",
        "message": "Data updated successfully",
        "data"   : {
            "id"         : item.id,
            "name"       : item.name,
            "description": item.description,
            "image"      : media_name(item.image),
            "active"     : item.active,
            "image_link" : media_url(item.image),
        },
        "error": {},
    }
