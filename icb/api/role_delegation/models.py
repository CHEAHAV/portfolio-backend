from icb.core.model import *


class ROLE_DELEGATION_PARENT():
    id                = Column(String(64), primary_key=True)
    delegator_user_id = Column(String(42), nullable=False, index=True)
    delegatee_user_id = Column(String(42), nullable=False, index=True)
    role_id           = Column(String(42), nullable=False, index=True)
    starts_at         = Column(DateTime, nullable=False)
    ends_at           = Column(DateTime)
    is_active         = Column(Boolean, default=True)
    reason            = Column(String(250))


class TBL_ROLE_DELEGATION(ROLE_DELEGATION_PARENT, CoreModel):
    pass


class TBL_ROLE_DELEGATION_UNAUTH(ROLE_DELEGATION_PARENT, CoreModel):
    pass


class TBL_ROLE_DELEGATION_HISTORY(ROLE_DELEGATION_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)


class TBL_ROLE_DELEGATION_DELETED(ROLE_DELEGATION_PARENT, CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)


class TBL_ROLE_DELEGATION_REJECTED(ROLE_DELEGATION_PARENT, CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)


class ROLE_DELEGATION_PERMISSION_PARENT():
    id         = Column(String(64), primary_key=True)
    parent_id  = Column(String(64), primary_key=True)
    module_id  = Column(String(64), nullable=False, index=True)
    permission = Column(String(250), nullable=False)


class TBL_ROLE_DELEGATION_PERMISSION(ROLE_DELEGATION_PERMISSION_PARENT, CoreModel):
    pass


class TBL_ROLE_DELEGATION_PERMISSION_UNAUTH(ROLE_DELEGATION_PERMISSION_PARENT, CoreModel):
    pass


class TBL_ROLE_DELEGATION_PERMISSION_HISTORY(ROLE_DELEGATION_PERMISSION_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)


class TBL_ROLE_DELEGATION_PERMISSION_DELETED(ROLE_DELEGATION_PERMISSION_PARENT, CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)


class TBL_ROLE_DELEGATION_PERMISSION_REJECTED(ROLE_DELEGATION_PERMISSION_PARENT, CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)
