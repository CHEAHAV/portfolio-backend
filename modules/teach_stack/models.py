from icb.core.model import *

class TEACH_STACK_PARENT():
    id          = Column(String(64), primary_key = True, index = True)
    name_left   = Column(String(255))
    image_left  = Column(String(255))
    name_right  = Column(String(255))
    image_right = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)

class TBL_TEACH_STACK(TEACH_STACK_PARENT, CoreModel):
    pass

class TBL_TEACH_STACK_UNAUTH(TEACH_STACK_PARENT, CoreModel):
    pass

class TBL_TEACH_STACK_HISTORY(TEACH_STACK_PARENT, CoreModel):
    re_version = Column(Integer, default = '0', primary_key = True)

class TBL_TEACH_STACK_DELETED(TEACH_STACK_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)

class TBL_TEACH_STACK_REJECTED(TEACH_STACK_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)
