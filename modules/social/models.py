from icb.core.model import *

class SOCIAL_PARENT():
    id          = Column(String(64), primary_key = True, index = True)
    name        = Column(String(255))
    icon        = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)

class TBL_SOCIAL(SOCIAL_PARENT, CoreModel):
    pass

class TBL_SOCIAL_UNAUTH(SOCIAL_PARENT, CoreModel):
    pass

class TBL_SOCIAL_HISTORY(SOCIAL_PARENT, CoreModel):
    re_version = Column(Integer, default = '0', primary_key = True)

class TBL_SOCIAL_DELETED(SOCIAL_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)

class TBL_SOCIAL_REJECTED(SOCIAL_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)
