from .models import *
from pydantic import BaseModel,EmailStr, root_validator, validator


class RoleSchema(BaseModel):
    id: str | None = None
    name: str
    name_lc: str | None = None
    is_superuser: bool
    description: str | None = None

class RoleModuleSchema(BaseModel):
    module_id: str
    permission: str

class RoleModuleListSchema(BaseModel):
    sub_item: list[RoleModuleSchema]  | None = None 
