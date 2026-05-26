from icb.core.model import *

class DISTRICT_PARENT():
    id          = Column(String(64), primary_key=True, index= True)
    name        = Column(String(100), nullable= False)
    name_lc     = Column(String(100), nullable = False)
    province_id = Column(String(64), nullable= False)
    description = Column(String(255))
    image       = Column(String(255), nullable= False)

class TBL_DISTRICT(DISTRICT_PARENT, CoreModel):
    pass

class TBL_DISTRICT_UNAUTH(DISTRICT_PARENT, CoreModel):
    pass

class TBL_DISTRICT_HISTORY(DISTRICT_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_DISTRICT_DELETED(DISTRICT_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)

class TBL_DISTRICT_REJECTED(DISTRICT_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)