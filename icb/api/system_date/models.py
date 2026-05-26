from sqlalchemy import Date

from icb.core.model import *

class SYSTEM_DATE_PARENT():
    id           = Column(String(64), primary_key=True)
    current_system_date = Column(Date)

class TBL_SYSTEM_DATE(SYSTEM_DATE_PARENT,CoreModel):
    pass

class TBL_SYSTEM_DATE_UNAUTH(SYSTEM_DATE_PARENT,CoreModel):
    pass

class TBL_SYSTEM_DATE_HISTORY(SYSTEM_DATE_PARENT,CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_SYSTEM_DATE_DELETED(SYSTEM_DATE_PARENT,CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

class TBL_SYSTEM_DATE_REJECTED(SYSTEM_DATE_PARENT,CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   
