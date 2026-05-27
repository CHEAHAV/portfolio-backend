import os
import math
from typing import Optional
from icb.core.db_session import get_db
from main import website
from fastapi import Depends, Query, Form, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from modules.location_id import generate_prefixed_id
from datetime import datetime
from modules.project.models import (
    TBL_PROJECT,
    TBL_PROJECT_DELETED,
    TBL_PROJECT_HISTORY,
    TBL_PROJECT_REJECTED,
    TBL_PROJECT_UNAUTH,
)
from modules.website.upload_utils import save_upload_with_unique_name

@website.get("/projects", tags=["Project"])
async def get_project(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_PROJECT).filter(TBL_PROJECT.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_PROJECT.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    base_url = os.getenv("APP_URL", "")

    data_list = [{
        'id'         : p.id,
        'name'       : p.name,
        'description': p.description,
        'duration'   : p.duration,
        'role'       : p.role,
        'platform'   : p.platform,
        'challenge'  : p.challenge,
        'image'      : p.image,
        "image_link" : f"{base_url}/static/images/Project/{p.image}" if p.image  is not None else "",
        'active'     : p.active
    } for p in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Project',
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


IMAGE_DIR = "static/images/Project"
os.makedirs(IMAGE_DIR, exist_ok=True)

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_PROJECT,
        TBL_PROJECT_UNAUTH,
        TBL_PROJECT_HISTORY,
        TBL_PROJECT_DELETED,
        TBL_PROJECT_REJECTED,
    ], "PRO")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result


def save_image(image: UploadFile) -> str:
    return save_upload_with_unique_name(image, IMAGE_DIR)

@website.post("/projects", tags=["Project"], status_code=201)
async def create_project(
    name        : str                  = Form(...,examples=[""]),
    description : str                  = Form(...,examples=[""]),
    duration    : str                  = Form(...,examples=[""]),
    role        : str                  = Form(...,examples=[""]),
    challenge   : str                  = Form(...,examples=[""]),
    platform    : str                  = Form(...,examples=[""]),
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
    new_item = TBL_PROJECT(
        id            = new_id,
        name          = name,
        description   = description,
        duration      = duration,
        role          = role,
        platform      = platform,
        challenge     = challenge,
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
        "title"  : "Project",
        "message": "Data created successfully",
        "data"   : {
            "id"         : new_item.id,
            "name"       : new_item.name,
            "description": new_item.description,
            "duration"   : new_item.duration,
            "role"       : new_item.role,
            "platform"   : new_item.platform,
            "challenge"  : new_item.challenge,
            "image"      : new_item.image,
            "active"     : new_item.active,
            "image_link" : f"{base_url}/static/images/Project/{new_item.image}" if new_item.image else "",
        },
        "error": {},
    }
