from icb.core.model import *

# Reset password table
class RESET_PASSWORD_PARENT():
    id                       = Column(String(64), primary_key=True)
    user_id                  = Column(String(64), nullable=False)
    password                 = Column(String(20), nullable=False)
    required_change_password = Column(Boolean, default=False)
    send_to_email            = Column(Boolean, default=False)
    note                     = Column(String(250), nullable=True)

class TBL_RESET_PASSWORD(RESET_PASSWORD_PARENT,CoreModel):
    pass

class TBL_RESET_PASSWORD_UNAUTH(RESET_PASSWORD_PARENT,CoreModel):
    pass

class TBL_RESET_PASSWORD_HISTORY(RESET_PASSWORD_PARENT,CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_RESET_PASSWORD_DELETED(RESET_PASSWORD_PARENT,CoreModel):
    pass

class TBL_RESET_PASSWORD_REJECTED(RESET_PASSWORD_PARENT,CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(String(30), default='', primary_key=True)
    