from .models import *
from pydantic import BaseModel, root_validator, validator
from icb.core.db import db
from icb.api.user.models import *
from icb.core.security import *

# The validation for module reset password
class ResetPasswordSchema(BaseModel):
    id              : str | None = None
    user_id         : str
    password        : str
    password_confirm: str
    note            : str | None = ''

    @validator('user_id', allow_reuse=True)
    def validate_user_id(cls, value: str):
        if not value:
            raise ValueError({'user_id':'User ID is required'})
        obj = db.query(TBL_USER).filter(TBL_USER.id == value).first()
        if obj is None:
            raise ValueError({'user_id':'This user is not found'})
        return value

    @root_validator(pre=False, allow_reuse=True, skip_on_failure=True)
    def check_password(cls, values: dict):
        pwd = values.get('password')
        pwd_confirm = values.get('password_confirm')

        if check_valid_password(pwd) != True:
            raise ValueError({'password':'Password is not strong. It must contain number, symbols, lowercase and uppercase letter'})

        if pwd != pwd_confirm:
            raise ValueError({'password_confirm':'Password confirm is not matched'})

        return values
