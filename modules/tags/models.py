from icb.core.model import *

class TAGS_PARENT():
    id          = Column(String(64), primary_key= True, index= True)
    name        = Column(String(64), nullable= False)
    description = Column(String(255), nullable = False)
    active      = Column(Boolean, default= True, nullable= False)

class TBL_TAGS(TAGS_PARENT, CoreModel):
    pass

class TBL_TAGS_UNAUTH(TAGS_PARENT, CoreModel):
    pass

class TBL_TAGS_HISTORY(TAGS_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_TAGS_DELETED(TAGS_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)

class TBL_TAGS_REJECTED(TAGS_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)
