from sqlalchemy import JSON

from icb.core.model import *

class NOTIFICATION_PARENT():
    id          = Column(String(64), primary_key=True, index=True)
    module_id   = Column(String(64))
    notify_type = Column(String(25))
    data        = Column(JSON)

class TBL_NOTIFICATION(NOTIFICATION_PARENT,CoreModel):
    pass

class TBL_NOTIFICATION_UNAUTH(NOTIFICATION_PARENT,CoreModel):
    pass

class TBL_NOTIFICATION_HISTORY(NOTIFICATION_PARENT,CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_NOTIFICATION_DELETED(NOTIFICATION_PARENT,CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

class TBL_NOTIFICATION_REJECTED(NOTIFICATION_PARENT,CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)

class TBL_USER_NOTIFICATION(CoreModel):
    id              = Column(Integer, primary_key=True, autoincrement=True)
    user_id         = Column(String(64), nullable=False, index=True)
    notification_id = Column(String(64), nullable=False, index=True)
    viewed_at       = Column(String(34))
   