from sqlalchemy import Date, Time

from icb.core.model import *

class STORE_PARENT():
    id              = Column(String(64), primary_key=True, index=True)
    name            = Column(String(100), nullable=False)
    name_lc         = Column(String(250))
    phone           = Column(String(18))
    email           = Column(String(40))
    manager_name    = Column(String(64))
    opening_date    = Column(Date)
    country_id      = Column(String(64))
    province_id     = Column(String(64))
    district_id     = Column(String(64))
    commune_id      = Column(String(64))
    village_id      = Column(String(64))
    street_no       = Column(String(50))
    house_no        = Column(String(50))
    lat_long        = Column(String(30))
    image           = Column(String(60))
    active          = Column(Boolean, default=True)
    open_hours      = Column(Time)
    close_hours     = Column(Time)
    account_id      = Column(String(64))
    qr_image        = Column(String(60))
    distance        = Column(Integer) # Meters

class TBL_STORE(STORE_PARENT,CoreModel):
    pass

class TBL_STORE_UNAUTH(STORE_PARENT,CoreModel):
    pass

class TBL_STORE_HISTORY(STORE_PARENT,CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_STORE_DELETED(STORE_PARENT,CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

class TBL_STORE_REJECTED(STORE_PARENT,CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   
