from icb.core.model import *

class COMMUNE_PARENT():
    id          = Column(String(64), primary_key= True, index= True)
    name        = Column(String(100), nullable = False)
    name_lc     = Column(String(100), nullable = False)
    district_id = Column(String(64), nullable = False)
    description = Column(String(255))
    image       = Column(String(255), nullable = False)

class TBL_COMMUNE(COMMUNE_PARENT, CoreModel):
    pass

class TBL_COMMUNE_UNAUTH(COMMUNE_PARENT, CoreModel):
    pass

class TBL_COMMUNE_HISTORY(COMMUNE_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_COMMUNE_DELETED(COMMUNE_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)

class TBL_COMMUNE_REJECTED(COMMUNE_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)