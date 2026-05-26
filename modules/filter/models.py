from icb.core.model import *

class FILTER_PARENT():
    id          = Column(String(64), primary_key = True, index = True)
    name        = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)

class TBL_FILTER(FILTER_PARENT, CoreModel):
    pass

class TBL_FILTER_UNAUTH(FILTER_PARENT, CoreModel):
    pass

class TBL_FILTER_HISTORY(FILTER_PARENT, CoreModel):
    re_version = Column(Integer, default = '0', primary_key = True)

class TBL_FILTER_DELETED(FILTER_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)

class TBL_FILTER_REJECTED(FILTER_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)
