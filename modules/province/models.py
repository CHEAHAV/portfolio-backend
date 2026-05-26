from icb.core.model import *

class PROVINCE_PARENT():
    id          = Column(String(64), primary_key=True, index= True)
    name        = Column(String(100), nullable= False)
    name_lc     = Column(String(100), nullable= False)
    country_id  = Column(String(64), nullable= False)
    description = Column(String(255))
    image       = Column(String(255), nullable= False)

class TBL_PROVINCE(PROVINCE_PARENT, CoreModel):
    pass

class TBL_PROVINCE_UNAUTH(PROVINCE_PARENT, CoreModel):
    pass

class TBL_PROVINCE_HISTORY(PROVINCE_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_PROVINCE_DELETED(PROVINCE_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)

class TBL_PROVINCE_REJECTED(PROVINCE_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)