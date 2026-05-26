from sqlalchemy import JSON, func

from icb.core.model import *
from passlib.hash import bcrypt

class USER_PARENT():
    id                 = Column(String(42), primary_key=True, index=True)
    first_name         = Column(String(100))
    last_name          = Column(String(100))
    email              = Column(String(100))
    username           = Column(String(50), unique=True, nullable=False)
    phone              = Column(String(15), nullable=False, unique=True, index=True)
    password           = Column(String(120))
    pin                = Column(String(120))
    photo              = Column(String(100))
    is_active          = Column(Boolean(), default=True)
    notification       = Column(Boolean(), default=False)
    two_factor         = Column(Boolean(), default=False)
    require_reset_password = Column(Boolean(), default=False)
    language           = Column(String(5), default='en')
    attempt            = Column(Integer, default=0)
    last_activity_at   = Column(DateTime)
    code             = Column(String(6), nullable=True)
    expires_at       = Column(DateTime,  nullable=True)

class TBL_USER(USER_PARENT,CoreModel):
    pass

class TBL_USER_UNAUTH(USER_PARENT,CoreModel):
    pass

class TBL_USER_HISTORY(USER_PARENT,CoreModel):
    re_version   =  Column(Integer, default='0', primary_key=True)
    username     = Column(String(50), unique=False, nullable=False)
    phone        = Column(String(15), nullable=False, unique=False, index=True)

class TBL_USER_DELETED(USER_PARENT,CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

class TBL_USER_REJECTED(USER_PARENT,CoreModel):
    re_version      = Column(Integer, default='0', primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)
    


class USER_LOCATION_ASSIGNMENT_PARENT():
    id                     = Column(String(42), primary_key=True)
    user_id                = Column(String(42), primary_key=True, nullable=False)
    accessible_company_id  = Column(String(42), nullable=False)
    accessible_branch_ids  = Column(String(420), nullable=False)
    default_branch_id      = Column(String(42), nullable=False)
    default_store_id       = Column(String(42), nullable=False)
    role_id                = Column(String(42), nullable=False)
    is_default             = Column(Boolean(), default=False)
    accessible_stores      = Column(JSONB) # {"branch_id1": {"default_store_id": "store_id", "accessible_store_ids": ["store_id1", "store_id2"]}, "branch_id2": {...}}

class TBL_USER_LOCATION_ASSIGNMENT(USER_LOCATION_ASSIGNMENT_PARENT,CoreModel):
    pass

class TBL_USER_LOCATION_ASSIGNMENT_UNAUTH(USER_LOCATION_ASSIGNMENT_PARENT,CoreModel):
    pass

class TBL_USER_LOCATION_ASSIGNMENT_HISTORY(USER_LOCATION_ASSIGNMENT_PARENT,CoreModel):
    re_version   =  Column(Integer, default='0', primary_key=True)

class TBL_USER_LOCATION_ASSIGNMENT_DELETED(USER_LOCATION_ASSIGNMENT_PARENT,CoreModel):
    re_version      = Column(Integer, default=0, primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)

class TBL_USER_LOCATION_ASSIGNMENT_REJECTED(USER_LOCATION_ASSIGNMENT_PARENT,CoreModel):
    re_version      = Column(Integer, default='0', primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)

class USER_CASH_ACCOUNT_PARENT():
    id           = Column(String(42), primary_key=True)
    parent_id    = Column(String(42), primary_key=True, nullable=False)
    company_id   = Column(String(42), nullable=False)
    branch_id    = Column(String(42), nullable=False)
    currency_id  = Column(String(42), nullable=False)
    account_id   = Column(String(42), nullable=False)

class TBL_USER_CASH_ACCOUNT(USER_CASH_ACCOUNT_PARENT,CoreModel):
    pass

class TBL_USER_CASH_ACCOUNT_UNAUTH(USER_CASH_ACCOUNT_PARENT,CoreModel):
    pass

class TBL_USER_CASH_ACCOUNT_HISTORY(USER_CASH_ACCOUNT_PARENT,CoreModel):
    re_version   =  Column(Integer, default='0', primary_key=True)

class TBL_USER_CASH_ACCOUNT_DELETED(USER_CASH_ACCOUNT_PARENT,CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

class TBL_USER_CASH_ACCOUNT_REJECTED(USER_CASH_ACCOUNT_PARENT,CoreModel):
    re_version      = Column(Integer, default='0', primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)

class USER_ROLE_PARENT():
    id          = Column(String(42), primary_key=True)
    parent_id   = Column(String(42), primary_key=True, nullable=False)
    role_id     = Column(String(42), nullable=False)

class TBL_USER_ROLE(USER_ROLE_PARENT,CoreModel):
    pass

class TBL_USER_ROLE_UNAUTH(USER_ROLE_PARENT,CoreModel):
    pass

class TBL_USER_ROLE_HISTORY(USER_ROLE_PARENT,CoreModel):
    re_version   =  Column(Integer, default='0', primary_key=True)

class TBL_USER_ROLE_DELETED(USER_ROLE_PARENT,CoreModel):
    re_version      = Column(Integer, default='0', primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)

class TBL_USER_ROLE_REJECTED(USER_ROLE_PARENT,CoreModel):
    re_version      = Column(Integer, default='0', primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)
    
class TBL_USER_DEVICE_TOKEN(CoreModel):
    id        = Column(Integer, primary_key=True, autoincrement=True)
    user_id   = Column(String(42), nullable=False)
    token     = Column(String(500))

class TBL_USER_ACTIVITY_LOG(Base):
    id        = Column(Integer, primary_key=True, autoincrement=True)
    user_id   = Column(String(42), nullable=False)
    action    = Column(String(100))
    module    = Column(String(50))
    log_info  = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(300))
    branch_id  = Column(String(42))
    company_id = Column(String(42))
    re_created_at = Column(DateTime, default=func.now())
    
class TBL_USER_LOGIN_TOKEN(CoreModel):
    id        = Column(Integer, primary_key=True, autoincrement=True)
    user_id   = Column(String(42), nullable=False)
    token     = Column(String(500))
    device    = Column(String(300))
    expire_at  = Column(DateTime)
    working_company_id = Column(String(42))
    working_branch_id  = Column(String(42))
    working_store_id   = Column(String(42))

class TBL_PHONE_OTP(CoreModel):
    id          = Column(Integer, primary_key=True, autoincrement=True)
    phone       = Column(String(14), nullable=False)
    otp         = Column(String(10))
    otp_count   = Column(Integer, default=0)
    confirmed   = Column(Boolean, default=False)
    next_otp_at = Column(DateTime)
    expire_at   = Column(DateTime)

class TBL_EMAIL_OTP(CoreModel):
    id          = Column(Integer, primary_key=True, autoincrement=True)
    email       = Column(String, index=True)
    otp         = Column(String)
    otp_count   = Column(Integer, default=0)
    confirmed   = Column(Boolean, default=False)
    expire_at   = Column(DateTime)
    next_otp_at = Column(DateTime)

class TBL_RECORD_LOCK(CoreModel):
    id          = Column(Integer, primary_key=True, autoincrement=True)
    module_name = Column(String(50))
    module_id   = Column(String(42))
    record_type = Column(String(10))
    locked_by   = Column(String(42))
    locked_at   = Column(DateTime)
