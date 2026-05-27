import os
from icb.core.db_session import get_db
from main import website
from fastapi import Depends, Query, Form, HTTPException
from sqlalchemy.orm import Session
import math
from modules.location_id import generate_prefixed_id
from datetime import datetime
from modules.study.models import (
    TBL_STUDY,
    TBL_STUDY_DELETED,
    TBL_STUDY_HISTORY,
    TBL_STUDY_REJECTED,
    TBL_STUDY_UNAUTH,
)

@website.get("/studies", tags=["Study"])
async def get_study(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_STUDY).filter(TBL_STUDY.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_STUDY.title\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1

    data_list = [{
        'id'         : c.id,
        'title'      : c.title,
        'sub_title'  : c.sub_title,
        'description': c.description,
        'date'       : c.date,
        'active'     : c.active
    } for c in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Study',
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


def generate_id(db: Session) -> str:
    result = generate_prefixed_id(db, [
        TBL_STUDY,
        TBL_STUDY_UNAUTH,
        TBL_STUDY_HISTORY,
        TBL_STUDY_DELETED,
        TBL_STUDY_REJECTED,
    ], "STD")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result

@website.post("/studies", tags=["Study"], status_code=201)
async def create_study(
    title  : str  = Form(...,examples=[""]),
    sub_title  : str  = Form(...,examples=[""]),
    description  : str  = Form(...,examples=[""]),
    date  : str  = Form(...,examples=[""]),
    active: bool                 = Form(True),
    db    : Session              = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Insert the new record
    new_item = TBL_STUDY(
        id            = new_id,
        title         = title,
        sub_title     = sub_title,
        description   = description,
        date          = date,
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
    return {
        "ok"     : True,
        "status" : 201,
        "title"  : "MyCore",
        "message": "Data created successfully",
        "data"   : {
            "id"         : new_item.id,
            "title"      : new_item.title,
            "sub_title"  : new_item.sub_title,
            "description": new_item.description,
            "date"       : new_item.date,
            "active"     : new_item.active,
        },
        "error": {},
    }


@website.put("/studies/{id}", tags=["Study"])
async def update_study(
    id         : str,
    title      : str     = Form(..., examples=[""]),
    sub_title  : str     = Form(..., examples=[""]),
    description: str     = Form(..., examples=[""]),
    date       : str     = Form(..., examples=[""]),
    active     : bool    = Form(True),
    db         : Session = Depends(get_db),
):
    item = db.query(TBL_STUDY).filter(TBL_STUDY.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Study not found")

    item.title       = title
    item.sub_title   = sub_title
    item.description = description
    item.date        = date
    item.active      = active
    item.re_updated_at = datetime.now()

    db.commit()
    db.refresh(item)
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Study",
        "message": "Data updated successfully",
        "data"   : {
            "id"         : item.id,
            "title"      : item.title,
            "sub_title"  : item.sub_title,
            "description": item.description,
            "date"       : item.date,
            "active"     : item.active,
        },
        "error": {},
    }
