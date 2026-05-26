from icb.core.model import *

# Import file table
class FILE_UPLOAD_PARENT():
    original_name = Column(String(500))
    file_name     = Column(String(100), nullable=False)
    folder        = Column(String(50))
    operation     = Column(String(5))
    module        = Column(String(50))
    module_id     = Column(String(64))
    is_private    = Column(Boolean, default=False)

class TBL_FILE_UPLOAD(FILE_UPLOAD_PARENT,CoreModel):
    pass

# class TBL_FILE_UPLOAD_UNAUTH(FILE_UPLOAD_PARENT,CoreModel):
#     pass

# class TBL_FILE_UPLOAD_HISTORY(FILE_UPLOAD_PARENT,CoreModel):
#     re_version = Column(Integer, default='0', primary_key=True)

# class TBL_FILE_UPLOAD_DELETED(FILE_UPLOAD_PARENT,CoreModel):
#     pass

# class TBL_FILE_UPLOAD_REJECTED(FILE_UPLOAD_PARENT,CoreModel):
#     re_version    = Column(Integer, default='0', primary_key=True)
#     re_deleted_at = Column(DateTime, primary_key=True)
    