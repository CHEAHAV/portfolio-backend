from icb.core.model import *

class CONTACT_ME_PARENT():
    id          = Column(String(64), primary_key = True, index = True)
    name        = Column(String(255))
    description = Column(String(255))
    icon        = Column(String(255))
    active      = Column(Boolean, default = True, nullable= False)

class TBL_CONTACT_ME(CONTACT_ME_PARENT, CoreModel):
    pass

class TBL_CONTACT_ME_UNAUTH(CONTACT_ME_PARENT, CoreModel):
    pass

class TBL_CONTACT_ME_HISTORY(CONTACT_ME_PARENT, CoreModel):
    re_version = Column(Integer, default = '0', primary_key = True)

class TBL_CONTACT_ME_DELETED(CONTACT_ME_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)

class TBL_CONTACT_ME_REJECTED(CONTACT_ME_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)
