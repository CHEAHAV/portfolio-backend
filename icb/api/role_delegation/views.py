from datetime import datetime
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from main import app
from icb.api.module.models import TBL_MODULE
from icb.api.role.models import TBL_ROLE, TBL_ROLE_MODULE
from icb.api.user.models import TBL_USER, TBL_USER_LOCATION_ASSIGNMENT
from icb.core.crud_api import CRUDAPI
from icb.core.db_session import get_db
from icb.core.lib import check_is_superuser
from icb.core.logger import logger
from icb.core.role_delegation import get_own_role_ids, permission_tokens
from icb.core.security import User, get_current_active_user
from icb.lib.render_api import ResponseModel
from .models import TBL_ROLE_DELEGATION, TBL_ROLE_DELEGATION_PERMISSION
from .schemas import RoleDelegationPermissionListSchema, RoleDelegationSchema


class ROLE_DELEGATION_CRUD_API(CRUDAPI):
    query_fields = ['delegator_user_id', 'delegatee_user_id', 'role_id', 'reason']

    def get_header(self):
        return [
            {"field": "id", "text": "ID"},
            {"field": "delegator_user_id", "text": "Delegator User ID"},
            {"field": "delegatee_user_id", "text": "Delegatee User ID"},
            {"field": "role_id", "text": "Role ID"},
            {"field": "starts_at", "text": "Starts At"},
            {"field": "ends_at", "text": "Ends At"},
            {"field": "is_active", "text": "Active"},
            {"field": "reason", "text": "Reason"},
        ]

    def get_list_query(self, model):
        return self.db.query(model)

    def get_header_sub(self):
        return {
            'permissions': [
                {"field": "id", "text": "ID"},
                {"field": "module_id", "text": "Module ID"},
                {"field": "name", "model": TBL_MODULE, "label": "module_name", "text": "Module Name"},
                {"field": "permission", "text": "Permission"},
            ]
        }

    def get_vsi_query(self, record_type=''):
        model = getattr(self.moduleList, str(self.sub_models['permissions'].__name__) + record_type)
        return {
            'permissions': self.db.query(model).outerjoin(TBL_MODULE, TBL_MODULE.id == model.module_id)
        }

    def _delegator_has_role(self, delegator_user_id, role_id):
        return self.db.query(TBL_USER_LOCATION_ASSIGNMENT.id).filter(
            TBL_USER_LOCATION_ASSIGNMENT.user_id == delegator_user_id,
            TBL_USER_LOCATION_ASSIGNMENT.role_id == role_id,
            TBL_USER_LOCATION_ASSIGNMENT.accessible_company_id == self.current_user.token_working_company_id,
        ).first()

    def _validate_permission_scope(self):
        rows = (self.sub_item or {}).get('permissions') or []
        if not rows:
            return False, {'permissions': 'At least one module permission must be selected'}

        for row in rows:
            module_id = row.get('module_id')
            requested_permissions = permission_tokens(row.get('permission'))
            if not module_id:
                return False, {'module_id': 'module_id is required'}
            if not requested_permissions:
                return False, {'permission': 'permission is required'}

            role_module = self.db.query(TBL_ROLE_MODULE).filter(
                TBL_ROLE_MODULE.parent_id == self.item.get('role_id'),
                TBL_ROLE_MODULE.module_id == module_id,
                TBL_ROLE_MODULE.company_id == self.current_user.token_working_company_id,
            ).first()
            if not role_module:
                return False, {module_id: 'Delegator role does not have access to this module'}

            allowed_permissions = permission_tokens(role_module.permission)
            if 'ALL' in allowed_permissions:
                continue

            invalid_permissions = [p for p in requested_permissions if p not in allowed_permissions]
            if invalid_permissions:
                return False, {
                    module_id: 'Permission %s is not allowed for delegator role' % ', '.join(invalid_permissions)
                }

        return True, ''

    def _validate_delegation(self):
        delegator_user_id = self.item.get('delegator_user_id') or self.current_user.id
        self.item['delegator_user_id'] = delegator_user_id

        if delegator_user_id == self.item.get('delegatee_user_id'):
            return False, {
                'delegatee_user_id': 'delegatee_user_id cannot be the same as delegator_user_id'
            }

        if not check_is_superuser(self.db, self.current_user) and delegator_user_id != self.current_user.id:
            return False, {
                'delegator_user_id': 'Only a superuser can create delegation for another delegator'
            }

        role_obj = self.db.query(TBL_ROLE).filter(
            TBL_ROLE.id == self.item.get('role_id'),
            TBL_ROLE.company_id == self.current_user.token_working_company_id,
        ).first()
        if not role_obj:
            return False, {'role_id': 'Role does not exist in the working company'}

        delegatee_obj = self.db.query(TBL_USER.id).filter(
            TBL_USER.id == self.item.get('delegatee_user_id')
        ).first()
        delegatee_assignment = self.db.query(TBL_USER_LOCATION_ASSIGNMENT.id).filter(
            TBL_USER_LOCATION_ASSIGNMENT.user_id == self.item.get('delegatee_user_id'),
            TBL_USER_LOCATION_ASSIGNMENT.accessible_company_id == self.current_user.token_working_company_id,
        ).first()
        if not delegatee_obj and not delegatee_assignment:
            return False, {'delegatee_user_id': 'Delegatee user does not exist'}

        if not self._delegator_has_role(delegator_user_id, self.item.get('role_id')):
            return False, {'role_id': 'Delegator user does not have this role in the working company'}

        if not check_is_superuser(self.db, self.current_user) and self.item.get('role_id') not in get_own_role_ids(self.db, self.current_user):
            return False, {'role_id': 'You can only delegate a role assigned to your own user'}

        starts_at = self.item.get('starts_at')
        ends_at = self.item.get('ends_at')
        if starts_at and ends_at and ends_at <= starts_at:
            return False, {'ends_at': 'ends_at must be greater than starts_at'}

        return self._validate_permission_scope()

    def before_save(self):
        return self._validate_delegation()

    def before_update(self):
        return self._validate_delegation()


crud = ROLE_DELEGATION_CRUD_API(
    'Role Delegation',
    'role-delegations',
    TBL_ROLE_DELEGATION,
    {'permissions': TBL_ROLE_DELEGATION_PERMISSION},
    schema=RoleDelegationSchema,
    sub_schema=RoleDelegationPermissionListSchema,
)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Role Delegation'])


@app.get('/api/v1/role-delegations/my-active', tags=['Role Delegation'])
def get_my_active_role_delegations(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    try:
        now = datetime.now()
        rows = db.query(TBL_ROLE_DELEGATION).filter(
            TBL_ROLE_DELEGATION.delegatee_user_id == current_user.id,
            TBL_ROLE_DELEGATION.company_id == current_user.token_working_company_id,
            TBL_ROLE_DELEGATION.is_active == True,
            TBL_ROLE_DELEGATION.starts_at <= now,
            (TBL_ROLE_DELEGATION.ends_at == None) | (TBL_ROLE_DELEGATION.ends_at >= now),
            (TBL_ROLE_DELEGATION.branch_id == None) |
            (TBL_ROLE_DELEGATION.branch_id == '') |
            (TBL_ROLE_DELEGATION.branch_id == current_user.token_working_branch_id),
        ).all()

        return ResponseModel(
            ok=True,
            status=200,
            title='Role Delegation',
            message='Active role delegations retrieved successfully',
            module='Role Delegation',
            data=jsonable_encoder(rows),
        )
    finally:
        db.close()


@app.post('/api/v1/role-delegations/{delegation_id}/revoke', tags=['Role Delegation'])
def revoke_role_delegation(
    delegation_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    try:
        obj = db.query(TBL_ROLE_DELEGATION).filter(
            TBL_ROLE_DELEGATION.id == delegation_id,
            TBL_ROLE_DELEGATION.company_id == current_user.token_working_company_id,
        ).first()
        if not obj:
            raise HTTPException(status_code=404, detail='Role delegation not found')

        if obj.delegator_user_id != current_user.id and not check_is_superuser(db, current_user):
            raise HTTPException(status_code=403, detail='Only the delegator or a superuser can revoke this delegation')

        obj.is_active = False
        obj.re_updated_by = current_user.id
        obj.re_updated_at = datetime.now()
        db.add(obj)
        db.commit()

        return ResponseModel(
            ok=True,
            status=200,
            title='Role Delegation',
            message='Role delegation revoked successfully',
            module='Role Delegation',
            data=jsonable_encoder(obj),
        )
    except Exception:
        db.rollback()
        logger.exception("[role_delegation] failed to revoke delegation_id=%s", delegation_id)
        raise
    finally:
        db.close()
