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
from modules.mycore.models import (
    TBL_MY_CORE,
    TBL_MY_CORE_DELETED,
    TBL_MY_CORE_HISTORY,
    TBL_MY_CORE_REJECTED,
    TBL_MY_CORE_UNAUTH,
)

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
            "image"      : m.image,
            "image_link" : f"{base_url}/static/images/MyCore/{m.image}" if m.image else "",
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
    if not image.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename")

    dest = os.path.join(IMAGE_DIR, image.filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(image.file, f)
    return image.filename

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
            "image"     : new_item.image,
            "active"    : new_item.active,
            "image_link": f"{base_url}/static/images/MyCore/{new_item.image}" if new_item.image else "",
        },
        "error": {},
    }