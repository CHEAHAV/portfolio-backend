from icb.core.model import *
from sqlalchemy import Text, Numeric

class SKILL_PARENT():
    id          = Column(String(64), primary_key = True, index = True)
    name        = Column(String(255))
    score       = Column(Numeric(8,2))
    description = Column(Text)
    image       = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)

class TBL_SKILL(SKILL_PARENT, CoreModel):
    pass

class TBL_SKILL_UNAUTH(SKILL_PARENT, CoreModel):
    pass

class TBL_SKILL_HISTORY(SKILL_PARENT, CoreModel):
    re_version = Column(Integer, default = '0', primary_key = True)

class TBL_SKILL_DELETED(SKILL_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)

class TBL_SKILL_REJECTED(SKILL_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)
