from icb.core.model import *
from sqlalchemy import Text

class MY_CORE_PARENT():
    id          = Column(String(64), primary_key = True, index = True)
    name        = Column(String(255))
    description = Column(Text)
    image       = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)

class TBL_MY_CORE(MY_CORE_PARENT, CoreModel):
    pass

class TBL_MY_CORE_UNAUTH(MY_CORE_PARENT, CoreModel):
    pass

class TBL_MY_CORE_HISTORY(MY_CORE_PARENT, CoreModel):
    re_version = Column(Integer, default = '0', primary_key = True)

class TBL_MY_CORE_DELETED(MY_CORE_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)

class TBL_MY_CORE_REJECTED(MY_CORE_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)
