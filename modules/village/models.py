from icb.core.model import *

class VILLAGE_PARENT():
    id          = Column(String(64), primary_key=True, index= True)
    name        = Column(String(100), nullable = False)
    name_lc     = Column(String(100), nullable= False)
    commune_id  = Column(String(64), nullable= False)
    description = Column(String(255))
    image       = Column(String(255), nullable= False)

class TBL_VILLAGE(VILLAGE_PARENT, CoreModel):
    pass

class TBL_VILLAGE_UNAUTH(VILLAGE_PARENT, CoreModel):
    pass

class TBL_VILLAGE_HISTORY(VILLAGE_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_VILLAGE_DELETED(VILLAGE_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)

class TBL_VILLAGE_REJECTED(VILLAGE_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)