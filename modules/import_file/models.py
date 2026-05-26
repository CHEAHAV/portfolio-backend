from icb.core.model import *

# Import file table
class IMPORT_FILE_PARENT():
    id         = Column(String(64), primary_key=True,)
    table_name = Column(String(64), nullable=False)
    type       = Column(String(20), nullable=False)
    note       = Column(String(250), nullable=True)

class TBL_IMPORT_FILE(IMPORT_FILE_PARENT,CoreModel):
    pass

class TBL_IMPORT_FILE_UNAUTH(IMPORT_FILE_PARENT,CoreModel):
    pass

class TBL_IMPORT_FILE_HISTORY(IMPORT_FILE_PARENT,CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_IMPORT_FILE_DELETED(IMPORT_FILE_PARENT,CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)

class TBL_IMPORT_FILE_REJECTED(IMPORT_FILE_PARENT,CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)
    