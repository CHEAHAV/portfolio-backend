import os
import math
from typing import Optional
from icb.core.db_session import get_db
from main import website
from fastapi import Depends, Query, Form, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from modules.location_id import generate_prefixed_id
from datetime import datetime
from modules.teach_stack.models import (
    TBL_TEACH_STACK,
    TBL_TEACH_STACK_DELETED,
    TBL_TEACH_STACK_HISTORY,
    TBL_TEACH_STACK_REJECTED,
    TBL_TEACH_STACK_UNAUTH,
)
from modules.website.upload_utils import media_name, media_url, upload_image_to_cloudinary

@website.get("/teach-stacks", tags=["TeachStack"])
async def get_teach_stack(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_TEACH_STACK).filter(TBL_TEACH_STACK.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_TEACH_STACK.id\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1

    base_url = os.getenv("APP_URL", "")

    data_list = [{
        'id'              : t.id,
        'name_left'       : t.name_left,
        'image_left'      : media_name(t.image_left),
        "image_left_link" : media_url(t.image_left),
        'name_right'      : t.name_right,
        'image_right'     : media_name(t.image_right),
        "image_right_link": media_url(t.image_right),
        'active'          : t.active
    } for t in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'TeachStack',
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


IMAGE_DIR = "static/images/TeachStack"
os.makedirs(IMAGE_DIR, exist_ok=True)

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_TEACH_STACK,
        TBL_TEACH_STACK_UNAUTH,
        TBL_TEACH_STACK_HISTORY,
        TBL_TEACH_STACK_DELETED,
        TBL_TEACH_STACK_REJECTED,
    ], "TST")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result


def save_image(image: UploadFile) -> str:
    return upload_image_to_cloudinary(image, "TeachStack")

@website.post("/teach-stacks", tags=["TeachStack"], status_code=201)
async def create_teach_stack(
    name_left  : str                  = Form(...,  examples=[""]),
    image_left : Optional[UploadFile] = File(None),
    name_right : str                  = Form(...,  examples=[""]),
    image_right: Optional[UploadFile] = File(None),
    active     : bool                 = Form(True, examples=[True]),
    db         : Session              = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Persist images (if provided)
    image_filename_left: Optional[str] = None
    if image_left and image_left.filename:
        image_filename_left = save_image(image_left)

    image_filename_right: Optional[str] = None
    if image_right and image_right.filename:
        image_filename_right = save_image(image_right)

    # 3. Insert the new record
    new_item = TBL_TEACH_STACK(
        id            = new_id,
        name_left     = name_left,
        image_left    = image_filename_left, 
        name_right    = name_right,
        image_right   = image_filename_right,
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
        "title"  : "TeachStack",
        "message": "Data created successfully",
        "data"   : {
            "id"              : new_item.id,
            "name_left"       : new_item.name_left,
            "image_left"      : media_name(new_item.image_left),
            "image_left_link" : media_url(new_item.image_left),
            "name_right"      : new_item.name_right,
            "image_right"     : media_name(new_item.image_right),
            "image_right_link": media_url(new_item.image_right),
            "active"          : new_item.active,
        },
        "error": {},
    }


@website.put("/teach-stacks/{id}", tags=["TeachStack"])
async def update_teach_stack(
    id         : str,
    name_left  : Optional[str]        = Form(None, examples=[""]),
    image_left : Optional[UploadFile] = File(None),
    name_right : Optional[str]        = Form(None, examples=[""]),
    image_right: Optional[UploadFile] = File(None),
    active     : Optional[bool]       = Form(None, examples=[True]),
    db         : Session              = Depends(get_db),
):
    item = db.query(TBL_TEACH_STACK).filter(TBL_TEACH_STACK.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="TeachStack not found")

    if name_left is not None:
        item.name_left = name_left
    if name_right is not None:
        item.name_right = name_right
    if active is not None:
        item.active = active
    item.re_updated_at = datetime.now()
    if image_left and image_left.filename:
        item.image_left = save_image(image_left)
    if image_right and image_right.filename:
        item.image_right = save_image(image_right)

    db.commit()
    db.refresh(item)

    base_url = os.getenv("APP_URL", "")
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "TeachStack",
        "message": "Data updated successfully",
        "data"   : {
            "id"              : item.id,
            "name_left"       : item.name_left,
            "image_left"      : media_name(item.image_left),
            "image_left_link" : media_url(item.image_left),
            "name_right"      : item.name_right,
            "image_right"     : media_name(item.image_right),
            "image_right_link": media_url(item.image_right),
            "active"          : item.active,
        },
        "error": {},
    }
