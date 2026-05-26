from icb.core.model import *
from sqlalchemy import Time, Text


class JOB_PARENT():
    id                 = Column(String(64), primary_key=True, index=True)
    title              = Column(String(64), nullable= False)
    department_id      = Column(String(64), nullable= False)
    province_id        = Column(String(64), nullable= False)
    district_id        = Column(String(64), nullable= False)
    commune_id         = Column(String(64), nullable= False)
    village_id         = Column(String(64), nullable= False)
    employment_type    = Column(String(64), nullable= False)
    position_available = Column(Integer, default=1)
    salary_range       = Column(String(128))
    work_start_time    = Column(Time, nullable= False)
    work_end_time      = Column(Time, nullable= False)
    urgent_flag        = Column(Boolean, default=True, nullable= False)
    role               = Column(Text, nullable= False)
    responsibilities   = Column(Text)
    qualifications     = Column(Text)
    status             = Column(String(64), default='OPEN')
    order              = Column(Integer)
    active             = Column(Boolean, default=True)

class TBL_JOB(JOB_PARENT, CoreModel):
    pass

class TBL_JOB_UNAUTH(JOB_PARENT, CoreModel):
    pass

class TBL_JOB_HISTORY(JOB_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_JOB_DELETED(JOB_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)

class TBL_JOB_REJECTED(JOB_PARENT, CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)
