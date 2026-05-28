from icb.core.model import *
from sqlalchemy import Text

class PROJECT_PARENT():
    id          = Column(String(64), primary_key = True, index = True)
    name        = Column(String(255))
    description = Column(Text)
    duration    = Column(String(255))
    role        = Column(String(255))
    platform    = Column(String(255))
    challenge   = Column(Text)
    project_url = Column(Text)
    image       = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)

class TBL_PROJECT(PROJECT_PARENT, CoreModel):
    pass

class TBL_PROJECT_UNAUTH(PROJECT_PARENT, CoreModel):
    pass

class TBL_PROJECT_HISTORY(PROJECT_PARENT, CoreModel):
    re_version = Column(Integer, default = '0', primary_key = True)

class TBL_PROJECT_DELETED(PROJECT_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)

class TBL_PROJECT_REJECTED(PROJECT_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)
