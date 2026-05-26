from pydantic import BaseModel
from datetime import time as dt_time

class JobSchema(BaseModel):
    id                 : str | None     = None
    title              : str
    department_id      : str
    province_id        : str
    district_id        : str
    commune_id         : str
    village_id         : str
    employment_type    : str
    position_available : int | None = None
    salary_range       : str | None = None
    work_start_time    : dt_time
    work_end_time      : dt_time
    urgent_flag        : bool
    role               : str
    responsibilities   : str | None = None
    qualifications     : str | None = None
    status             : str
    order              : int | None = None
    active             : bool | None = None