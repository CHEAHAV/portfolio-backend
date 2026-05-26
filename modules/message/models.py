from icb.core.model import *
from sqlalchemy import Text

class MESSAGE_PARENT():
    id     = Column(String(64), primary_key = True, index = True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255))
    subject = Column(String(255))
    message = Column(Text)
    active = Column(Boolean, default = True, nullable= False)

class TBL_MESSAGE(MESSAGE_PARENT, CoreModel):
    pass

class TBL_MESSAGE_UNAUTH(MESSAGE_PARENT, CoreModel):
    pass

class TBL_MESSAGE_HISTORY(MESSAGE_PARENT, CoreModel):
    re_version = Column(Integer, default = '0', primary_key = True)

class TBL_MESSAGE_DELETED(MESSAGE_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)

class TBL_MESSAGE_REJECTED(MESSAGE_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)
