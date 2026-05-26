from icb.core.model import CoreModel
from sqlalchemy import Column, String, DateTime, Integer

class COLOR_PARENT(): 
    id   = Column(String(42), primary_key=True)
    name = Column(String(100), nullable=False)
    

class TBL_COLOR(COLOR_PARENT, CoreModel): 
    pass

class TBL_COLOR_UNAUTH(COLOR_PARENT, CoreModel): 
    pass

class TBL_COLOR_HISTORY(COLOR_PARENT, CoreModel): 
    re_version = Column(Integer, default=0, primary_key=True)

class TBL_COLOR_DELETED(COLOR_PARENT, CoreModel): 
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)

class TBL_COLOR_REJECTED(COLOR_PARENT,CoreModel): 
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)
