from sqlalchemy import JSON

from icb.core.model import *

class SYNC_SETTING_PARENT():
    id = Column(String(64), primary_key=True, index=True)
    module_name = Column(String(255))
    model_name = Column(String(255))
    enable_sync = Column(Boolean, default=False)
    sub_model_sync_include = Column(JSON, default='[]')

class TBL_SYNC_SETTING(SYNC_SETTING_PARENT, CoreModel):
    pass

class TBL_SYNC_SETTING_UNAUTH(SYNC_SETTING_PARENT, CoreModel):
    pass

class TBL_SYNC_SETTING_HISTORY(SYNC_SETTING_PARENT, CoreModel):
    re_version = Column(Integer, default=0, primary_key=True)

class TBL_SYNC_SETTING_DELETED(SYNC_SETTING_PARENT, CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

class TBL_SYNC_SETTING_REJECTED(SYNC_SETTING_PARENT,CoreModel):
    re_version      = Column(Integer, default=0, primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)


class SYNC_CONDITION_PARENT():
    id = Column(String(64), primary_key=True, index=True)
    parent_id = Column(String(64), primary_key=True)
    condition_type = Column(String(10))  # 'model' or 'function'
    condition = Column(String(255))  # Field name or function name
    operator = Column(String(10))
    value = Column(JSON)  # Value to compare against
    logic = Column(String(10), default='AND')
    group_id = Column(Integer)
    args = Column(JSON, default='{}')  # Arguments for functions

class TBL_SYNC_CONDITION(SYNC_CONDITION_PARENT, CoreModel):
    pass

class TBL_SYNC_CONDITION_UNAUTH(SYNC_CONDITION_PARENT, CoreModel):
    pass

class TBL_SYNC_CONDITION_HISTORY(SYNC_CONDITION_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_SYNC_CONDITION_DELETED(SYNC_CONDITION_PARENT, CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

class TBL_SYNC_CONDITION_REJECTED(SYNC_CONDITION_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)