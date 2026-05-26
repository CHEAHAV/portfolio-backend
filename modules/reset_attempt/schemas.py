from .models import *
from pydantic import BaseModel, validator
from icb.core.db import db
from icb.api.user.models import *
from icb.core.security import *

# The validation for module reset attempt
class ResetAttemptSchema(BaseModel):
    id     : str | None = None
    user_id: str
    note   : str | None = ''

    @validator('user_id', allow_reuse=True)
    def validate_user_id(cls, value: str):
        if not value:
            raise ValueError({'user_id':'User ID is required'})
        obj = db.query(TBL_USER).filter(TBL_USER.id == value).first()
        if obj is None:
            raise ValueError({'user_id':'This user is not found'})
        return value
