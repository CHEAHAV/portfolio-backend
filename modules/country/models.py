from icb.core.model import *

class COUNTRY_PARENT():
    id          = Column(String(64), primary_key= True, index= True)
    name        = Column(String(100), nullable= False)
    name_lc     = Column(String(100), nullable = False)
    description = Column(String(255))
    image       = Column(String(255), nullable= False)

class TBL_COUNTRY(COUNTRY_PARENT, CoreModel):
    pass

class TBL_COUNTRY_UNAUTH(COUNTRY_PARENT, CoreModel):
    pass

class TBL_COUNTRY_HISTORY(COUNTRY_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_COUNTRY_DELETED(COUNTRY_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)

class TBL_COUNTRY_REJECTED(COUNTRY_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)