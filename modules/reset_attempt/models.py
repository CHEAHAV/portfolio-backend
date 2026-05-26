from icb.core.model import *

# Reset attempt table
class RESET_ATTEMPT_PARENT():
    id      = Column(String(64), primary_key=True)
    user_id = Column(String(64), nullable=False)
    note    = Column(String(250), nullable=True)

class TBL_RESET_ATTEMPT(RESET_ATTEMPT_PARENT,CoreModel):
    pass

class TBL_RESET_ATTEMPT_UNAUTH(RESET_ATTEMPT_PARENT,CoreModel):
    pass

class TBL_RESET_ATTEMPT_HISTORY(RESET_ATTEMPT_PARENT,CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_RESET_ATTEMPT_DELETED(RESET_ATTEMPT_PARENT,CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(String(30), default='', primary_key=True)

class TBL_RESET_ATTEMPT_REJECTED(RESET_ATTEMPT_PARENT,CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(String(30), default='', primary_key=True)
    