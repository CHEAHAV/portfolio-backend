from icb.core.model import *

class SYSTEM_SETTING_PARENT():
    id                              = Column(String(64), primary_key=True)
    token_timeout                   = Column(Integer, default=0)
    login_attempt                   = Column(Integer, default=0)
    otp_limit                       = Column(Integer, default=0)
    system_online                   = Column(Boolean, default=True, nullable=False)
    default_password                = Column(String(64), default='Def@u1tPa$$w0rd')
    telegram_bot_token              = Column(String(255), default='')
    telegram_chat_id                = Column(String(255), default='')

class TBL_SYSTEM_SETTING(SYSTEM_SETTING_PARENT, CoreModel):
    pass

class TBL_SYSTEM_SETTING_UNAUTH(SYSTEM_SETTING_PARENT, CoreModel):
    pass

class TBL_SYSTEM_SETTING_HISTORY(SYSTEM_SETTING_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_SYSTEM_SETTING_DELETED(SYSTEM_SETTING_PARENT, CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

class TBL_SYSTEM_SETTING_REJECTED(SYSTEM_SETTING_PARENT, CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   
