from .models import *
from pydantic import BaseModel,EmailStr, root_validator, validator


class WorkflowSchema(BaseModel):
    id          : str | None = None
    module_id   : str
    condition   : str
    description : str

class WorkflowDetailSchema(BaseModel):
    id             : str | None = None
    role_id        : str
    num_of_auth    : int | None = 0
    auth_order     : int | None = 0
    auth_status    : str | None = None
    role_condition : str | None = None

class WorkflowListSchema(BaseModel):
    detail : list[WorkflowDetailSchema]  | None = None 

