import math
from types import SimpleNamespace

from fastapi import Body, Depends, HTTPException, Query
from sqlalchemy import Boolean, DateTime, Integer, or_
from sqlalchemy.orm import Session

from icb.api.company.models import (
    TBL_COMPANY,
    TBL_COMPANY_DELETED,
    TBL_COMPANY_HISTORY,
    TBL_COMPANY_REJECTED,
    TBL_COMPANY_UNAUTH,
)
from icb.core.db_session import get_db
from main import app
from modules.commune.models import TBL_COMMUNE
from modules.country.models import TBL_COUNTRY
from modules.district.models import TBL_DISTRICT
from modules.location_id import assign_prefixed_id
from modules.location_join import lookup_name
from modules.province.models import TBL_PROVINCE
from modules.village.models import TBL_VILLAGE
from modules.website.upload_utils import media_url
import os


FIELD_MAP = {
    "phone_number": "phone",
    "phone_number_2": "phone_2",
}


def _clean_company_value(column, value):
    if value == "":
        if isinstance(column.type, (Integer, DateTime, Boolean)):
            return None
        if column.nullable:
            return None
    return value


def _apply_company_item(row, item, db: Session | None = None, is_create=False):
    columns = TBL_COMPANY.__table__.columns

    for key, value in item.items():
        mapped_key = FIELD_MAP.get(key, key)
        if mapped_key not in columns:
            continue
        setattr(row, mapped_key, _clean_company_value(columns[mapped_key], value))

    if is_create:
        if not getattr(row, "id", None) and db:
            crud_context = SimpleNamespace(db=db, item={})
            assign_prefixed_id(crud_context, [
                TBL_COMPANY,
                TBL_COMPANY_UNAUTH,
                TBL_COMPANY_HISTORY,
                TBL_COMPANY_DELETED,
                TBL_COMPANY_REJECTED,
            ], "CMP")
            row.id = crud_context.item["id"]
        if not getattr(row, "company_id", None):
            row.company_id = row.id


def _lookup_name(db, model, value):
    prefix_map = {
        TBL_COUNTRY: "COU",
        TBL_PROVINCE: "PRO",
        TBL_DISTRICT: "DIS",
        TBL_COMMUNE: "COM",
        TBL_VILLAGE: "VL",
    }
    return lookup_name(db, model, value, prefix_map.get(model))


def _company_logo_link(row):
    return media_url(row.logo)


def _serialize_company(row, db: Session | None = None):
    country_name = province_name = district_name = commune_name = village_name = parent_name = ""
    if db:
        country_name = _lookup_name(db, TBL_COUNTRY, row.country_id)
        province_name = _lookup_name(db, TBL_PROVINCE, row.province_id)
        district_name = _lookup_name(db, TBL_DISTRICT, row.district_id)
        commune_name = _lookup_name(db, TBL_COMMUNE, row.commune_id)
        village_name = _lookup_name(db, TBL_VILLAGE, row.village_id)
        parent_name = _lookup_name(db, TBL_COMPANY, row.parent_company_id)

    return {
        "id": row.id,
        "name": row.name,
        "name_lc": row.name_lc,
        "description": row.description,
        "description_lc": row.description_lc,
        "logo": row.logo,
        "logo_link": _company_logo_link(row),
        "phone": row.phone,
        "phone_number": row.phone,
        "phone_2": row.phone_2,
        "phone_number_2": row.phone_2,
        "telegram": row.telegram,
        "email": row.email,
        "website": row.website,
        "facebook": row.facebook,
        "youtube": row.youtube,
        "country_id": row.country_id,
        "country_name": country_name,
        "province_id": row.province_id,
        "province_name": province_name,
        "district_id": row.district_id,
        "district_name": district_name,
        "commune_id": row.commune_id,
        "commune_name": commune_name,
        "village_id": row.village_id,
        "village_name": village_name,
        "street_no": row.street_no,
        "house_no": row.house_no,
        "lat_long": row.lat_long,
        "registration_number": row.registration_number,
        "vat_tin": row.vat_tin,
        "is_group_holding": row.is_group_holding,
        "parent_company_id": row.parent_company_id,
        "parent_name": parent_name,
        "re_version": row.re_version,
        "re_status": row.re_status,
        "re_created_at": row.re_created_at,
    }


def _response(data, page=1, size=10, total=0):
    return {
        "ok": True,
        "status": 200,
        "title": "Company",
        "message": "Data retrieved successfully",
        "data": {
            "lists": data,
            "meta_data": {
                "total": total,
                "total_page": math.ceil(total / size) if size else 1,
                "current_page": page,
                "size": size,
            },
        },
        "error": {},
    }


@app.get("/api/v1/wb/company", tags=["Company"])
async def get_companies(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(TBL_COMPANY)
    if search:
        query = query.filter(or_(TBL_COMPANY.name.ilike(f"%{search}%"), TBL_COMPANY.name_lc.ilike(f"%{search}%")))

    total = query.count()
    rows = query.order_by(TBL_COMPANY.name.asc()).offset((page - 1) * size).limit(size).all()
    return _response([_serialize_company(row, db) for row in rows], page, size, total)


@app.get("/api/v1/wb/company/query-list", tags=["Company"])
@app.get("/api/v1/wb/company/query", tags=["Company"])
async def query_companies(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return await get_companies(page=page, size=size, search=search, db=db)


@app.get("/api/v1/wb/company/new", tags=["Company"])
async def new_company():
    return {
        "ok": True,
        "status": 200,
        "title": "Company",
        "message": "Data retrieved successfully",
        "data": {
            "item": {},
            "sub_items": {},
        },
        "error": {},
    }


@app.get("/api/v1/wb/company/view/{id}", tags=["Company"])
async def view_company(id: str, db: Session = Depends(get_db)):
    row = db.query(TBL_COMPANY).filter(TBL_COMPANY.id == id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Company not found")

    return {
        "ok": True,
        "status": 200,
        "title": "Company",
        "message": "Data retrieved successfully",
        "data": {
            "item": _serialize_company(row, db),
            "sub_items": {},
        },
        "error": {},
    }


@app.post("/api/v1/wb/company", tags=["Company"])
async def create_company(body: dict = Body(default={}), db: Session = Depends(get_db)):
    item = body.get("item", body)
    row = TBL_COMPANY()

    _apply_company_item(row, item, db=db, is_create=True)

    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "ok": True,
        "status": 200,
        "title": "Company",
        "message": "Company created successfully",
        "data": _serialize_company(row, db),
        "error": {},
    }


@app.put("/api/v1/wb/company/{id}", tags=["Company"])
async def update_company(id: str, body: dict = Body(default={}), db: Session = Depends(get_db)):
    row = db.query(TBL_COMPANY).filter(TBL_COMPANY.id == id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Company not found")

    item = body.get("item", body)
    _apply_company_item(row, item)

    db.commit()
    db.refresh(row)

    return {
        "ok": True,
        "status": 200,
        "title": "Company",
        "message": "Company updated successfully",
        "data": _serialize_company(row, db),
        "error": {},
    }


@app.delete("/api/v1/wb/company/{id}", tags=["Company"])
async def delete_company(id: str, db: Session = Depends(get_db)):
    row = db.query(TBL_COMPANY).filter(TBL_COMPANY.id == id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Company not found")

    db.delete(row)
    db.commit()

    return {
        "ok": True,
        "status": 200,
        "title": "Company",
        "message": "Company deleted successfully",
        "data": {},
        "error": {},
    }
