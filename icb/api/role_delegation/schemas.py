from datetime import datetime

from pydantic import BaseModel, field_validator


class RoleDelegationSchema(BaseModel):
    id: str | None = None
    delegator_user_id: str | None = None
    delegatee_user_id: str
    role_id: str
    starts_at: datetime
    ends_at: datetime | None = None
    is_active: bool = True
    reason: str | None = None

    @field_validator('ends_at')
    @classmethod
    def validate_end_after_start(cls, ends_at, info):
        starts_at = info.data.get('starts_at')
        if starts_at and ends_at and ends_at <= starts_at:
            raise ValueError('ends_at must be greater than starts_at')
        return ends_at


class RoleDelegationPermissionSchema(BaseModel):
    id: str | None = None
    module_id: str
    permission: str


class RoleDelegationPermissionListSchema(BaseModel):
    permissions: list[RoleDelegationPermissionSchema] | None = None
