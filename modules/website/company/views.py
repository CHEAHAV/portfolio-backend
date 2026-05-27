from icb.api.company.models import TBL_COMPANY
from icb.core.db_session import get_db
from main import website
from fastapi import Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import math
from modules.website.upload_utils import media_name, media_url

@website.get("/companys", tags=["Company"])
async def get_company(
    page: int     = Query(default=1, ge=1),
    size: int     = Query(default=10, ge=1),
    db  : Session = Depends(get_db)
):
    base_query = db.query(TBL_COMPANY).filter()

    total   = base_query.count()
    results = base_query.order_by(TBL_COMPANY.name\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1
    
    data_list = [{
        'id'                 : com.id,
        'name'               : com.name,
        'name_lc'            : com.name_lc,
        'description'        : com.description,
        'description_lc'     : com.description_lc,
        'logo'               : media_name(com.logo),
        'logo_link'          : media_url(com.logo),
        'banner'             : media_name(com.banner),
        'banner_link'        : media_url(com.banner),
        'phone'              : com.phone,
        'phone2'             : com.phone_2,
        'telegram'           : com.telegram,
        'email'              : com.email,
        'website'            : media_name(com.website),
        "website_link"       : media_url(com.website),
        'facebook'           : media_name(com.facebook),
        "facebook_link"      : media_url(com.facebook),
        'youtube'            : media_name(com.youtube),
        "youtube_link"       : media_url(com.youtube),
        'country_id'         : com.country_id,
        'province_id'        : com.province_id,
        'district_id'        : com.district_id,
        'commune_id'         : com.commune_id,
        'village_id'         : com.village_id,
        'street_no'          : com.street_no,
        'house_no'           : com.house_no,
        'lat_long'           : com.lat_long,
        'registration_number': com.registration_number,
        'vat_tin'            : com.vat_tin
    } for com in results]

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Campany',
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


@website.put("/companys/{id}", tags=["Company"])
async def update_company(
    id: str,
    body: dict = Body(default={}),
    db: Session = Depends(get_db)
):
    row = db.query(TBL_COMPANY).filter(TBL_COMPANY.id == id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Company not found")

    item = body.get("item", body)
    columns = TBL_COMPANY.__table__.columns
    for key, value in item.items():
        if key in columns:
            setattr(row, key, value)

    db.commit()
    db.refresh(row)

    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Campany',
        'message': 'Data updated successfully',
        'data'   : item,
        'error'  : {}
    }
