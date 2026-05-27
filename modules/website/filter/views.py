import os
from icb.core.db_session import get_db
from main import website
from fastapi import Depends, Query, Form, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import math
from modules.location_id import generate_prefixed_id
from datetime import datetime
from modules.filter.models import (
    TBL_FILTER,
    TBL_FILTER_DELETED,
    TBL_FILTER_HISTORY,
    TBL_FILTER_REJECTED,
    TBL_FILTER_UNAUTH,
)

@website.get("/filters", tags=["Filter"])
async def get_filter(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_FILTER).filter(TBL_FILTER.active == True)

    total   = base_query.count()
    results = base_query.order_by(TBL_FILTER.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1

    data_list = [{
        'id'    : f.id,
        'name'  : f.name,
        'active': f.active
    } for f in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Filter',
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
        TBL_FILTER,
        TBL_FILTER_UNAUTH,
        TBL_FILTER_HISTORY,
        TBL_FILTER_DELETED,
        TBL_FILTER_REJECTED,
    ], "FIL")
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to generate a unique ID")
    return result

@website.post("/filters", tags=["Filter"], status_code=201)
async def create_filter(
    name  : str  = Form(...,examples=[""]),
    active: bool                 = Form(True),
    db    : Session              = Depends(get_db),
):
    # 1. Generate a unique, prefixed ID
    new_id = generate_id(db)

    # 2. Insert the new record
    new_item = TBL_FILTER(
        id            = new_id,
        name         = name,
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
        "title"  : "Filter",
        "message": "Data created successfully",
        "data"   : {
            "id"         : new_item.id,
            "name"      : new_item.name,
            "active"     : new_item.active,
        },
        "error": {},
    }


@website.put("/filters/{id}", tags=["Filter"])
async def update_filter(
    id    : str,
    name  : str     = Form(..., examples=[""]),
    active: bool    = Form(True),
    db    : Session = Depends(get_db),
):
    item = db.query(TBL_FILTER).filter(TBL_FILTER.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Filter not found")

    item.name = name
    item.active = active
    item.re_updated_at = datetime.now()

    db.commit()
    db.refresh(item)
    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Filter",
        "message": "Data updated successfully",
        "data"   : {
            "id"    : item.id,
            "name"  : item.name,
            "active": item.active,
        },
        "error": {},
    }
