from icb.core.model import *

class ROLE_PARENT():
    __table_args__ = {'extend_existing': True}
    id           = Column(String(64), primary_key=True)
    name         = Column(String(100), nullable=False)
    name_lc      = Column(String(100))
    is_superuser = Column(Boolean, default=False)
    description  = Column(String(100))

class TBL_ROLE(ROLE_PARENT,CoreModel):
    pass

class TBL_ROLE_UNAUTH(ROLE_PARENT,CoreModel):
    pass

class TBL_ROLE_HISTORY(ROLE_PARENT,CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_ROLE_DELETED(ROLE_PARENT,CoreModel):
    pass

class TBL_ROLE_REJECTED(ROLE_PARENT,CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(String(30), default='', primary_key=True)

class ROLE_MODULE_PARENT():
    __table_args__ = {'extend_existing': True}
    id          = Column(String(64), primary_key=True)
    parent_id   = Column(String(64), primary_key=True)
    module_id   = Column(String(64))
    permission  = Column(String(100), nullable=False)

class TBL_ROLE_MODULE(ROLE_MODULE_PARENT,CoreModel):
    pass

class TBL_ROLE_MODULE_UNAUTH(ROLE_MODULE_PARENT,CoreModel):
    pass

class TBL_ROLE_MODULE_HISTORY(ROLE_MODULE_PARENT,CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_ROLE_MODULE_DELETED(ROLE_MODULE_PARENT,CoreModel):
    pass

class TBL_ROLE_MODULE_REJECTED(ROLE_MODULE_PARENT,CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(String(30), default='', primary_key=True)
