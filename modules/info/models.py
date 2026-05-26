from icb.core.model import *
from sqlalchemy import Text

class INFO_PARENT():
    id          = Column(String(64), primary_key = True, index = True)
    name        = Column(String(255))
    description = Column(Text)
    image       = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)

class TBL_INFO(INFO_PARENT, CoreModel):
    pass

class TBL_INFO_UNAUTH(INFO_PARENT, CoreModel):
    pass

class TBL_INFO_HISTORY(INFO_PARENT, CoreModel):
    re_version = Column(Integer, default = '0', primary_key = True)

class TBL_INFO_DELETED(INFO_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)

class TBL_INFO_REJECTED(INFO_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)
