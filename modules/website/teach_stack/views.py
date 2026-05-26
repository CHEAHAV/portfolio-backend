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
from modules.teach_stack.models import (
    TBL_TEACH_STACK,
    TBL_TEACH_STACK_DELETED,
    TBL_TEACH_STACK_HISTORY,
    TBL_TEACH_STACK_REJECTED,
    TBL_TEACH_STACK_UNAUTH,
)

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
        'image_left'      : t.image_left,
        "image_left_link" : f"{base_url}/static/images/TeachStack/{t.image_left}" if t.image_left is not None else "",
        'name_right'      : t.name_right,
        'image_right'     : t.image_right,
        "image_right_link": f"{base_url}/static/images/TeachStack/{t.image_right}" if t.image_right is not None else "",
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
    if not image.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename")

    dest = os.path.join(IMAGE_DIR, image.filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(image.file, f)
    return image.filename

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
            "image_left"      : new_item.image_left,
            "image_left_link" : f"{base_url}/static/images/TeachStack/{new_item.image_left}" if new_item.image_left else "",
            "name_right"      : new_item.name_right,
            "image_right"     : new_item.image_right,
            "image_right_link": f"{base_url}/static/images/TeachStack/{new_item.image_right}" if new_item.image_right else "",
            "active"          : new_item.active,
        },
        "error": {},
    }