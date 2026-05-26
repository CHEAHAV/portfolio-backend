from icb.core.model import *
from sqlalchemy import Text

class CAREER_PARENT():
    id          = Column(String(64), primary_key = True, index = True)
    title       = Column(String(255))
    sub_title   = Column(String(255))
    description = Column(Text)
    date        = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)

class TBL_CAREER(CAREER_PARENT, CoreModel):
    pass

class TBL_CAREER_UNAUTH(CAREER_PARENT, CoreModel):
    pass

class TBL_CAREER_HISTORY(CAREER_PARENT, CoreModel):
    re_version = Column(Integer, default = '0', primary_key = True)

class TBL_CAREER_DELETED(CAREER_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)

class TBL_CAREER_REJECTED(CAREER_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)
