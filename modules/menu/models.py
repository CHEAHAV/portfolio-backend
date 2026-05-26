from icb.core.model import *

class SUB_MENU_PARENT():
    __table_args__ = {'extend_existing' : True}
    company_id     = Column(String(64))
    
class TBL_SUB_MENU(SUB_MENU_PARENT,CoreModel):
    pass

class TBL_SUB_MENU_UNAUTH(SUB_MENU_PARENT,CoreModel):
    pass

class TBL_SUB_MENU_HISTORY(SUB_MENU_PARENT,CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_SUB_MENU_DELETED(SUB_MENU_PARENT,CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

class TBL_SUB_MENU_REJECTED(SUB_MENU_PARENT,CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)
