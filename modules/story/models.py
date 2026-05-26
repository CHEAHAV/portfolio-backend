from icb.core.model import *
from sqlalchemy  import Text

class STORY_PARENT():
    id          = Column(String(64), primary_key = True, index = True)
    title       = Column(String(255))
    description = Column(Text)
    icon_name   = Column(String(255))
    icon        = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)

class TBL_STORY(STORY_PARENT, CoreModel):
    pass

class TBL_STORY_UNAUTH(STORY_PARENT, CoreModel):
    pass

class TBL_STORY_HISTORY(STORY_PARENT, CoreModel):
    re_version = Column(Integer, default = '0', primary_key = True)

class TBL_STORY_DELETED(STORY_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)

class TBL_STORY_REJECTED(STORY_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)
