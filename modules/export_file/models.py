from icb.core.model import *

# Export file table
class EXPORT_FILE_PARENT():
    id         = Column(String(64), primary_key=True)
    table_name = Column(String(64), nullable=False)
    note       = Column(String(250), nullable=True)

class TBL_EXPORT_FILE(EXPORT_FILE_PARENT,CoreModel):
    pass

class TBL_EXPORT_FILE_UNAUTH(EXPORT_FILE_PARENT,CoreModel):
    pass

class TBL_EXPORT_FILE_HISTORY(EXPORT_FILE_PARENT,CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_EXPORT_FILE_DELETED(EXPORT_FILE_PARENT,CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)

class TBL_EXPORT_FILE_REJECTED(EXPORT_FILE_PARENT,CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)
    