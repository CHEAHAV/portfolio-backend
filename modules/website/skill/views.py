import os
from typing import Optional
from icb.core.db_session import get_db
from main import website
from fastapi import Depends, Query, Form, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import math
from modules.location_id import generate_prefixed_id
from datetime import datetime
from modules.skill.models import (
    TBL_SKILL,
    TBL_SKILL_DELETED,
    TBL_SKILL_HISTORY,
    TBL_SKILL_REJECTED,
    TBL_SKILL_UNAUTH,
)
from modules.website.upload_utils import save_upload_with_unique_name

@website.get("/skills", tags=["Skill"])
async def get_skill(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_SKILL).filter(TBL_SKILL.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_SKILL.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1

    base_url = os.getenv("APP_URL", "")

    data_list = [{
        'id'         : s.id,
        'name'       : s.name,
        'score'      : s.score,
        'description': s.description,
        'image'      : s.image,
        "image_link" : f"{base_url}/static/images/Skill/{s.image}" if s.image  is not None else "",
        'active'     : s.active
    } for s in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Skill',
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

IMAGE_DIR = "static/images/Skill"
os.makedirs(IMAGE_DIR, exist_ok=True)

def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_SKILL,
        TBL_SKILL_UNAUTH,
        TBL_SKILL_HISTORY,
        TBL_SKILL_DELETED,
        TBL_SKILL_REJECTED,
    ], "CAR")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result


def save_image(image: UploadFile) -> str:
    return save_upload_with_unique_name(image, IMAGE_DIR)

@website.post("/skills", tags=["Skill"], status_code=201)
async def create_skill(
    name        : str                  = Form(...,examples=[""]),
    score       : float                = Form(...,examples=[""]),
    description : str                  = Form(...,examples=[""]),
    image       : Optional[UploadFile] = File(None),
    active      : bool                 = Form(True),
    db          : Session              = Depends(get_db),
):
    if score < 0 or score > 5:
        raise HTTPException(status_code=400, detail="Score must be between 0 and 5")

    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Persist the image (if provided)
    image_filename: Optional[str] = None
    if image and image.filename:
        image_filename = save_image(image)

    # 3. Insert the new record
    new_item = TBL_SKILL(
        id            = new_id,
        name          = name,
        score         = score,
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
        "title"  : "Skill",
        "message": "Data created successfully",
        "data"   : {
            "id"         : new_item.id,
            "name"       : new_item.name,
            "score"      : new_item.score,
            "description": new_item.description,
            "image"      : new_item.image,
            "image_link" : f"{base_url}/static/images/Skill/{new_item.image}" if new_item.image else "",
            "active"     : new_item.active,
        },
        "error": {},
    }


@website.put("/skills/{id}", tags=["Skill"])
async def update_skill(
    id         : str,
    name       : str                  = Form(..., examples=[""]),
    score      : float                = Form(..., examples=[""]),
    description: str                  = Form(..., examples=[""]),
    image      : Optional[UploadFile] = File(None),
    active     : bool                 = Form(True),
    db         : Session              = Depends(get_db),
):
    if score < 0 or score > 5:
        raise HTTPException(status_code=400, detail="Score must be between 0 and 5")

    item = db.query(TBL_SKILL).filter(TBL_SKILL.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Skill not found")

    item.name = name
    item.score = score
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
        "title"  : "Skill",
        "message": "Data updated successfully",
        "data"   : {
            "id"         : item.id,
            "name"       : item.name,
            "score"      : item.score,
            "description": item.description,
            "image"      : item.image,
            "image_link" : f"{base_url}/static/images/Skill/{item.image}" if item.image else "",
            "active"     : item.active,
        },
        "error": {},
    }
