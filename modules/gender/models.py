from icb.core.model import *

class GENDER_PARENT():
    id          = Column(String(64), primary_key=True, index= True)
    description = Column(String(10), nullable=False)
    description_lc = Column(String(10), nullable=False)
    order       = Column(Integer)
    icon        = Column(String(255))

class TBL_GENDER(GENDER_PARENT, CoreModel):
    pass

class TBL_GENDER_UNAUTH(GENDER_PARENT, CoreModel):
    pass

class TBL_GENDER_HISTORY(GENDER_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_GENDER_DELETED(GENDER_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

class TBL_GENDER_REJECTED(GENDER_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   
