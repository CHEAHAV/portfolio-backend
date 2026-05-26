from icb.core.model import *

class DEPARTMENT_PARENT():
    id          = Column(String(64), primary_key= True, index= True)
    name        = Column(String(64), nullable = False)
    description = Column(String(255), nullable = False)
    image       = Column(String(255), nullable = False)
    active      = Column(Boolean, default = True, nullable= False)

class TBL_DEPARTMENT(DEPARTMENT_PARENT, CoreModel):
    pass

class TBL_DEPARTMENT_UNAUTH(DEPARTMENT_PARENT, CoreModel):
    pass

class TBL_DEPARTMENT_HISTORY(DEPARTMENT_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_DEPARTMENT_DELETED(DEPARTMENT_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)

class TBL_DEPARTMENT_REJECTED(DEPARTMENT_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)