from sqlalchemy import Text

from icb.core.model import *

class COMPANY_PARENT():
    id                  = Column(String(42), primary_key=True, index=True)
    name                = Column(String(250), nullable=False)
    name_lc             = Column(String(250), nullable=False)
    description         = Column(Text())
    description_lc      = Column(Text())
    logo                = Column(String(200))
    banner              = Column(String(200))
    phone               = Column(String(150))
    phone_2             = Column(String(150))
    telegram            = Column(String(25))
    email               = Column(String(100))
    website             = Column(String(60))
    facebook            = Column(String(100))
    youtube             = Column(String(100))
    country_id          = Column(String(42), nullable=False)
    province_id         = Column(String(42), nullable=False)
    district_id         = Column(String(42))
    commune_id          = Column(String(42))
    village_id          = Column(String(42))
    street_no           = Column(String(50))
    house_no            = Column(String(50))
    lat_long            = Column(String(30))
    registration_number = Column(String(25))
    vat_tin             = Column(String(25))
    is_group_holding    = Column(Boolean, default=False)
    parent_company_id   = Column(String(64))
    

class TBL_COMPANY(COMPANY_PARENT,CoreModel):
    pass

class TBL_COMPANY_UNAUTH(COMPANY_PARENT,CoreModel):
    pass

class TBL_COMPANY_HISTORY(COMPANY_PARENT,CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_COMPANY_DELETED(COMPANY_PARENT,CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

class TBL_COMPANY_REJECTED(COMPANY_PARENT,CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)

class COMPANY_DOCUMENT_PARENT():
    id = Column(String(64), primary_key=True, index=True)
    parent_id = Column(String(64))
    doc_type = Column(String(100))
    doc_name = Column(String(255))
    attachment = Column(String(60))
    note = Column(Text)

class TBL_COMPANY_DOCUMENT(COMPANY_DOCUMENT_PARENT, CoreModel):
    pass

class TBL_COMPANY_DOCUMENT_UNAUTH(COMPANY_DOCUMENT_PARENT, CoreModel):
    pass

class TBL_COMPANY_DOCUMENT_HISTORY(COMPANY_DOCUMENT_PARENT, CoreModel):
    re_version = Column(Integer, default=0, primary_key=True)

class TBL_COMPANY_DOCUMENT_DELETED(COMPANY_DOCUMENT_PARENT, CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

class TBL_COMPANY_DOCUMENT_REJECTED(COMPANY_DOCUMENT_PARENT, CoreModel):
    re_version = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)
