from icb.core.model import *
from sqlalchemy import Text

class JOB_APPLICATION_PARENT():
    id           = Column(String(64), primary_key=True, index= True)
    parent_id    = Column(String(64), nullable= False)
    full_name    = Column(String(64), nullable= False)
    email        = Column(String(255), nullable= False)
    phone_number = Column(String(50), nullable= False)
    gender       = Column(String(32), nullable= False)
    portfolio    = Column(Text, nullable= False)
    linkedin_url = Column(String(500))
    github_url   = Column(String(500))
    other_url    = Column(String(500))
    about_you    = Column(Text)
    upload_cv    = Column(Text, nullable= False)
    status       = Column(String(30), nullable= False)

class TBL_JOB_APPLICATION(JOB_APPLICATION_PARENT, CoreModel):
    pass

class TBL_JOB_APPLICATION_UNAUTH(JOB_APPLICATION_PARENT, CoreModel):
    pass

class TBL_JOB_APPLICATION_HISTORY(JOB_APPLICATION_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_JOB_APPLICATION_DELETED(JOB_APPLICATION_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)

class TBL_JOB_APPLICATION_REJECTED(JOB_APPLICATION_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)
