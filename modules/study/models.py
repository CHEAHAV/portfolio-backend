from icb.core.model import *
from sqlalchemy import Text

class STUDY_PARENT():
    id          = Column(String(64), primary_key = True, index = True)
    title       = Column(String(255))
    sub_title   = Column(String(255))
    description = Column(Text)
    date        = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)

class TBL_STUDY(STUDY_PARENT, CoreModel):
    pass

class TBL_STUDY_UNAUTH(STUDY_PARENT, CoreModel):
    pass

class TBL_STUDY_HISTORY(STUDY_PARENT, CoreModel):
    re_version = Column(Integer, default = '0', primary_key = True)

class TBL_STUDY_DELETED(STUDY_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)

class TBL_STUDY_REJECTED(STUDY_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)
