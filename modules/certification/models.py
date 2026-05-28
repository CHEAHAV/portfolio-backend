from icb.core.model import *
from sqlalchemy import Date, Text
class CERTIFICATION_PARENT():
    id              = Column(String(64), primary_key = True, index = True)
    name            = Column(String(255))
    title           = Column(String(255))
    issuer          = Column(String(255))
    date_earned     = Column(Date)
    credential_id   = Column(String(255))
    certificate_url = Column(Text)
    icon            = Column(String(255))
    active          = Column(Boolean, default = True, nullable= False)

class TBL_CERTIFICATION(CERTIFICATION_PARENT, CoreModel):
    pass

class TBL_CERTIFICATION_UNAUTH(CERTIFICATION_PARENT, CoreModel):
    pass

class TBL_CERTIFICATION_HISTORY(CERTIFICATION_PARENT, CoreModel):
    re_version = Column(Integer, default = '0', primary_key = True)

class TBL_CERTIFICATION_DELETED(CERTIFICATION_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)

class TBL_CERTIFICATION_REJECTED(CERTIFICATION_PARENT, CoreModel):
    re_version    = Column(Integer, default = '0', primary_key = True)
    re_deleted_at = Column(DateTime, primary_key = True)
