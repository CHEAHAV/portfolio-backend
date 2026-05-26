import math
import string
import time, uuid, os, random, json

from datetime import datetime, date
from typing import Annotated
from fastapi import Query, Request, FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
from resizeimage import resizeimage
from sqlalchemy import Boolean, DateTime, Integer, or_, text, and_

from main import app, Body
from icb.api.dashboard.models import TBL_DASHBOARD_ITEM, TBL_DASHBOARDS
from icb.api.role.models import TBL_ROLE, TBL_ROLE_MODULE
from icb.api.branch.models import TBL_BRANCH
from icb.api.user.models import *
from icb.core.crud_api import *
from icb.core.security import *
import icb.core.lib as core_lib
from .schemas import *
from icb.core.lib import get_lang as ___, get_module_id
from icb.api.company.models import TBL_COMPANY
from icb.lib.render_api import response_msg, response_data
from itertools import chain
import qrcode
from io import BytesIO
from icb.lib.render_api import ResponseModel
from icb.core.lib import check_is_superuser
from icb.core.role_delegation import get_active_delegated_permission_rows, get_effective_role_ids
from icb.lib.join_helper import JoinHelper
from icb.lib.keycloak_helper import *
from icb.core.crud_keycloak import CODE_TTL_MINUTES, _check_system_restriction
from .MFA import _send_otp_email_local
from icb.core.crud_keycloak import KeycloakCRUDAPI
from datetime import datetime, timedelta
from icb.core.crud_keycloak import (
    _get_admin_token, _find_user_by_username, _verify_email_matches,
    _keycloak_send_reset_link, _generate_code, _send_otp_email,
    _keycloak_set_password, _ok, _field, CODE_TTL_MINUTES
)
from modules.location_id import assign_prefixed_id

class USER_CRUD_API(CRUDAPI):
    query_fields = ['first_name','last_name']

    def _get_sub_items(self):
        return getattr(self, 'sub_item', None) or getattr(self, 'sub_items', None) or {}

    def _extract_roles(self):
        roles = self.item.pop('roles', None) or self.item.pop('role_list', None) or []
        sub_items = self._get_sub_items()
        if not roles and isinstance(sub_items, dict):
            roles = sub_items.get('role_list') or sub_items.get('roles') or []

        if isinstance(roles, dict):
            roles = [roles]

        return roles or []

    def _value_id(self, value):
        if isinstance(value, dict):
            return value.get('value') or value.get('id') or ''
        return value or ''

    def _branch_ids(self, value):
        if isinstance(value, list):
            return ','.join(str(self._value_id(item)) for item in value if self._value_id(item))
        return str(self._value_id(value)) if self._value_id(value) else ''

    def _prepare_roles(self, roles):
        default_company = getattr(self.current_user, 'token_working_company_id', None) or self.item.get('company_id') or 'SYSTEM'
        default_branch = self._value_id(self.item.get('working_branch')) or getattr(self.current_user, 'token_working_branch_id', None) or self.item.get('branch_id') or 'HQ'
        access_branches = self._branch_ids(self.item.get('access_branches')) or default_branch
        default_store = getattr(self.current_user, 'working_store_id', None) or self.item.get('store_id') or 'HS'

        prepared_roles = []
        for index, role in enumerate(roles):
            if not isinstance(role, dict):
                role = {'role_id': role}

            role_id = self._value_id(role.get('role_id'))
            if not role_id:
                continue

            prepared_roles.append({
                **role,
                'role_id': role_id,
                'accessible_company_id': self._value_id(role.get('accessible_company_id')) or default_company,
                'accessible_branch_ids': self._branch_ids(role.get('accessible_branch_ids')) or access_branches,
                'default_branch_id': self._value_id(role.get('default_branch_id')) or default_branch,
                'default_store_id': self._value_id(role.get('default_store_id')) or default_store,
                'accessible_stores': role.get('accessible_stores') or {},
                'is_default': role.get('is_default') if role.get('is_default') is not None else index == 0,
            })

        return prepared_roles

    def normalize_user_item(self):
        item = self.item
        columns = TBL_USER.__table__.columns

        for key in list(item.keys()):
            if key not in columns:
                item.pop(key, None)
                continue

            value = item.get(key)
            if value == "":
                column = columns[key]
                if isinstance(column.type, (Integer, DateTime, Boolean)) or column.nullable:
                    item[key] = None

        if not item.get('id'):
            assign_prefixed_id(self, [
                TBL_USER,
                TBL_USER_UNAUTH,
                TBL_USER_HISTORY,
                TBL_USER_DELETED,
                TBL_USER_REJECTED,
            ], "USR")

        if not item.get('company_id'):
            item['company_id'] = getattr(self.current_user, 'token_working_company_id', None) or 'SYSTEM'

        if not item.get('branch_id'):
            item['branch_id'] = getattr(self.current_user, 'token_working_branch_id', None) or 'HQ'

        if not item.get('store_id'):
            item['store_id'] = getattr(self.current_user, 'working_store_id', None) or 'HS'

        item.setdefault('language', 'en')
        item.setdefault('attempt', 0)
        item.setdefault('is_active', True)
        item.setdefault('notification', False)
        item.setdefault('two_factor', False)
        item.setdefault('require_reset_password', False)

    def before_save(self, lang='en'):
        print('==== Body : ', self.item)

        roles = self._prepare_roles(self._extract_roles())
        self.item.pop('account_list', None)

        id = self.item.get('id', None)
        if self.item.get('password') and not str(self.item.get('password')).startswith('$2'):
            self.item.update({'password': get_password_hash(self.item['password']) })
        else:
            if not self.item.get('password'):
                self.item.pop('password', None)

        self.normalize_user_item()
        
        errors = {}
        obj = self.db.query(TBL_USER).filter(TBL_USER.username==self.item['username']).first()
        if obj and obj.id != id:
            errors.update({'username':'Username is already exist'})
            
        obj = self.db.query(TBL_USER).filter(TBL_USER.phone==self.item['phone']).first()
        if obj and obj.id != id:
            errors.update({'phone':'Phone number is already exist'})
        # self.item.update({'phone': nomalize_phone(self.item['phone']) if self.item['phone'] else None})
            
        if self.item.get('email'):
            obj = self.db.query(TBL_USER).filter(TBL_USER.email==self.item['email']).first()
            if obj and obj.id != id:
                errors.update({'email':'Email is already exist'})

            
        if errors:
            return False, errors
        
        user_id = self.item.get('id', None)

        try: 

            if roles:
                self.item['roles'] = roles
                valid, message = self.add_user_location_assignment()
                if not valid:
                    return False, message

            return True, ''
        except Exception as e: 
            db.rollback()
            return False, str(e)
        
    def before_update(self):
        id = self.item.get('id', None)
        roles = self._prepare_roles(self._extract_roles())
        self.item.pop('account_list', None)

        if self.item.get('password') and not str(self.item.get('password')).startswith('$2'):
            self.item.update({'password': get_password_hash(self.item['password']) })
        else:
            if not self.item.get('password'):
                self.item.pop('password', None)

        self.normalize_user_item()
            
        errors = {}
        obj = self.db.query(TBL_USER).filter(TBL_USER.id!=self.id).filter(TBL_USER.username==self.item['username']).first()
        if obj and obj.id != id:
            errors.update({'username':'Username is already exist'})
            
        obj = self.db.query(TBL_USER).filter(TBL_USER.id!=self.id).filter(TBL_USER.phone==self.item['phone']).first()
        if obj and obj.id != id:
            errors.update({'phone':'Phone number is already exist'})
            
        if self.item.get('email'):
            obj = self.db.query(TBL_USER).filter(TBL_USER.id!=self.id).filter(TBL_USER.email==self.item['email']).first()
            if obj and obj.id != id:
                errors.update({'email':'Email is already exist'})
        # self.item.update({'phone': nomalize_phone(self.item['phone']) if self.item['phone'] else None})

        if roles:
            self.item['roles'] = roles
            valid, message = self.add_user_location_assignment(is_update=True)
            if not valid:
                return False, message
          
        if errors:
            raise ValueError(errors)
         
        return True, ''

    def get_header(self):
        return [
            {"field": "id", "text": "ID"},
            {"field": "first_name", "text": "First Name"},
            {"field": "last_name", "text": "Last Name"},
            {"field": "email", "text": "Email"},
            {"field": "username", "text": "Username"},
            {"field": "phone", "text": "Phone Number"},
            {"field": "is_active", "text": "Active"},
            {"field": "language", "text": "Language"},
            {"field": "notification", "text": "Notification"},
            {"field": "two_factor", "text": "Two Factor"},
            {"field": "require_reset_password", "text": "Require Reset Password"},
            {"field": "name", "model": TBL_COMPANY, "label": "base_company_name", "text": "Base Company Name"},
            {"field": "name", "model": TBL_BRANCH, "label": "base_branch_name", "text": "Base Branch Name"},
        ]
        
    def get_list_query(self, model):
        query = JoinHelper(self.db, model)\
            .outerjoin(TBL_BRANCH, TBL_BRANCH.id == model.branch_id)\
            .outerjoin(TBL_COMPANY, TBL_COMPANY.id == model.company_id)\
            .outerjoin(TBL_USER_LOCATION_ASSIGNMENT, TBL_USER_LOCATION_ASSIGNMENT.user_id == model.id)\
            .outerjoin(TBL_ROLE, TBL_ROLE.id == TBL_USER_LOCATION_ASSIGNMENT.role_id)\
            .get_query()
            # .outerjoin(TBL_GENDER, TBL_GENDER.id == model.gender)\
        
        return query

    def set_default(self, is_default): 
        if is_default: 
            self.db.query(TBL_USER_LOCATION_ASSIGNMENT)\
                .filter(TBL_USER_LOCATION_ASSIGNMENT.user_id == self.item.get('user_id'))\
                .update({'is_default': False})

    def add_user_location_assignment(self, is_update=False): 
        now = datetime.now()
        roles = [i for i in self.item.get('roles', [])]

        if not roles: 
            return False, 'Role is required'

        try: 
            if roles: 
                data_row = []
                ids = []
                for role in roles: 
                    id = get_module_id(db, 'UserLocationAssignment', self.current_user.token_working_company_id)
                    ids.append(id)
                    role.update({'id': id, 'user_id': self.item.get('id')})

                    audit = {
                        "re_created_at"    : now,
                        "re_created_by"    : self.current_user.id,
                        "re_updated_at"    : now,
                        "re_updated_by"    : self.current_user.id,
                        "system_date"       : now,
                        "branch_id"        : self.current_user.token_working_branch_id,
                        "company_id"       : self.current_user.token_working_company_id,
                        "authorization": [
                            {
                                "id": self.current_user.id,
                                "status": "APPROVED",
                                "datetime": str(now)
                            }
                        ],
                    }

                    data_row.append({
                        **role,
                        **audit
                    })
                if is_update: 
                    db.query(TBL_USER_LOCATION_ASSIGNMENT).filter(
                        TBL_USER_LOCATION_ASSIGNMENT.user_id == self.item.get('id'),
                        TBL_USER_LOCATION_ASSIGNMENT.company_id == self.current_user.token_working_company_id,
                        # TBL_USER_LOCATION_ASSIGNMENT.branch_id == self.current_user.token_working_branch_id,
                    ).delete()
                    
                db.bulk_insert_mappings(TBL_USER_LOCATION_ASSIGNMENT, data_row)


                db.commit()
        except Exception as e: 
            db.rollback()
            return False, str(e)
        
        # Remove from schema to insert into user
        self.item.pop('roles', None)

        return True, ''

    

    def before_view_response(self, item):
        item_dict = item.get('item',{})
        item_dict.pop('password', None)
        item_dict.pop('pin', None)

        # Get user role base current user company
        query = db.query(
            TBL_USER_LOCATION_ASSIGNMENT.id,
            TBL_USER_LOCATION_ASSIGNMENT.role_id, 
            TBL_ROLE.name, 
            TBL_USER_LOCATION_ASSIGNMENT.is_default, 
            TBL_USER_LOCATION_ASSIGNMENT.accessible_company_id, 
            TBL_USER_LOCATION_ASSIGNMENT.accessible_branch_ids, 
            TBL_USER_LOCATION_ASSIGNMENT.default_branch_id,
            TBL_USER_LOCATION_ASSIGNMENT.default_store_id,
            TBL_COMPANY.name.label('accessible_company_name'),
            TBL_BRANCH.name.label('default_branch_name'),
        )\
            .outerjoin(TBL_ROLE, TBL_ROLE.id == TBL_USER_LOCATION_ASSIGNMENT.role_id)\
            .outerjoin(TBL_COMPANY, TBL_COMPANY.id == TBL_USER_LOCATION_ASSIGNMENT.accessible_company_id)\
            .outerjoin(TBL_BRANCH, TBL_BRANCH.id == TBL_USER_LOCATION_ASSIGNMENT.default_branch_id)\
            .filter(
                TBL_USER_LOCATION_ASSIGNMENT.user_id == item_dict.get('id'),
                TBL_USER_LOCATION_ASSIGNMENT.company_id == self.current_user.token_working_company_id,
                TBL_USER_LOCATION_ASSIGNMENT.branch_id == self.current_user.token_working_branch_id,
            ).all()
        
        def get_branch_data(company_id, branch_id):
            branch = self.db.query(TBL_BRANCH.id, TBL_BRANCH.name).filter(
                TBL_BRANCH.company_id == company_id,TBL_BRANCH.id == branch_id
            ).first()
            return { 'value': branch.id, 'title': branch.name } if branch else { 'value': '', 'title': ''}
        
        roles = [{
                'id'                     : i.id,
                'role_id'                : i.role_id,
                'role_name'              : i.name,
                'accessible_company_id'  : i.accessible_company_id,
                'accessible_company_name': i.accessible_company_name,
                'accessible_branch_ids'  : [get_branch_data(i.accessible_company_id,bid) for bid in (i.accessible_branch_ids).split(',')],
                'default_branch_id'      : i.default_branch_id,
                'default_branch_name'    : i.default_branch_name,
                'default_store_id'       : i.default_store_id,
                'is_default'             : i.is_default,
            } for i 
            in query 
        ]
        item_dict.update({'roles': roles})
        return item

    def before_response(self, items, obj=None): 
        user_ids = [i.get('id') for i in items]

        query = self.db.query(TBL_USER_LOCATION_ASSIGNMENT).filter(
            TBL_USER_LOCATION_ASSIGNMENT.user_id.in_(user_ids)
        ).all()
        
        for item in items: 
            roles = [{
                    'role_id': i.role_id,
                    'accessible_company_id': i.accessible_company_id,
                    'accessible_branch_ids': [bid for bid in (i.accessible_branch_ids).split(',')],
                    'default_branch_id': i.default_branch_id,
                } for i 
                in query 
                if i.user_id == item.get('id')
            ]
            item.update({'roles': roles})
        
        return items
            
    
    

crud = USER_CRUD_API('User', 'users', TBL_USER, { }, schema=UserSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['User'])


@app.get("/api/v1/wb/users/new", tags=["User"])
async def new_user():
    return {
        "ok": True,
        "status": 200,
        "title": "User",
        "message": "Data retrieved successfully",
        "data": {
            "item": {},
            "sub_items": {},
        },
        "error": {},
    }


class USER_LOCATION_ASSIGNMENT_CRUD_API(CRUDAPI):

    def get_header(self):
        return  [
            {'field': 'id', "text":"ID"}, 
            {'field': 'accessible_company_id', "text":"Accessible Company"}, 
            {'field': 'name', 'model': TBL_COMPANY, 'label': 'name', "text":"Company Name"},
            {'field': 'accessible_branch_ids', "text":"Accessible Branches"}, 
            {'field': 'default_branch_id', "text":"Default Branch"}, 
            {'field': 'name', 'model': TBL_BRANCH, 'label': 'default_branch_name', "text":"Default Branch Name"},
            {'field': 'role_id', 'text': 'Rold ID'},
            {'field': 'name', 'model': TBL_ROLE, 'label': 'role_name', "text":"Role Name"},
            {'field': 'is_default', 'text': 'Is Default'},
            {'field': 'user_id', 'text': 'User ID'},
        ]
    
    def get_list_query(self, model):
        return self.db.query(model).\
            outerjoin(TBL_COMPANY, TBL_COMPANY.id == model.accessible_company_id).\
            outerjoin(TBL_BRANCH, and_(TBL_BRANCH.id == model.default_branch_id,TBL_BRANCH.company_id == model.accessible_company_id)).\
            outerjoin(TBL_ROLE, TBL_ROLE.id == model.role_id)

    def before_view_response(self, item):
        item_dict = item.get('item',{})
        branch_ids = item_dict.get('accessible_branch_ids','').split(',')
        branches = self.db.query(
            TBL_BRANCH.name.label('title')
        ).\
        filter(TBL_BRANCH.id.in_(branch_ids)).all()
        branches = ','.join([branch.title for branch in branches])
        item_dict.update({'accessible_branches': branches})
        return item

    def set_default(self, is_default): 
        if is_default: 
            self.db.query(TBL_USER_LOCATION_ASSIGNMENT)\
                .filter(TBL_USER_LOCATION_ASSIGNMENT.user_id == self.item.get('user_id'))\
                .update({'is_default': False})

    def before_save(self): 
        user_id = self.item.get('user_id')
        company_id = self.item.get('accessible_company_id')

        query = db.query(TBL_USER_LOCATION_ASSIGNMENT).\
            filter(TBL_USER_LOCATION_ASSIGNMENT.user_id == user_id).\
            filter(TBL_USER_LOCATION_ASSIGNMENT.accessible_company_id == company_id).first()

        if query: 
            return False, 'User already has a location assignment for this company'

        self.set_default(self.item.get('is_default', False))

        return True, ''

    def before_update(self): 
        self.set_default(self.item.get('is_default', False))

        return True, ''
    
crud = USER_LOCATION_ASSIGNMENT_CRUD_API('UserLocationAssignment', 'user-location-assignment', TBL_USER_LOCATION_ASSIGNMENT, {}, schema=UserLocatinAssignmentSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['User'])

def get_default_role_id(db):
    role = db.query(TBL_ROLE).filter(TBL_ROLE.id == 'SUPERUSER').first()
    if role:
        return role.id

    role = db.query(TBL_ROLE).filter(TBL_ROLE.id == 'ADMIN').first()
    if role:
        return role.id

    role = db.query(TBL_ROLE).first()
    return role.id if role else ''

def ensure_default_user_location(db, user):
    ula_obj = db.query(TBL_USER_LOCATION_ASSIGNMENT).\
        filter(TBL_USER_LOCATION_ASSIGNMENT.user_id == user.id).\
        filter(TBL_USER_LOCATION_ASSIGNMENT.is_default == True).\
        first()

    if ula_obj:
        return ula_obj

    dnow = datetime.now()
    company_id = getattr(user, 'company_id', None) or 'SYSTEM'
    branch_id = getattr(user, 'branch_id', None) or 'HQ'
    store_id = getattr(user, 'store_id', None) or 'HS'
    role_id = get_default_role_id(db)

    ula_obj = TBL_USER_LOCATION_ASSIGNMENT(**{
        'id'                     : str(uuid.uuid4()),
        'user_id'                : user.id,
        'accessible_company_id'  : company_id,
        'accessible_branch_ids'  : branch_id,
        'default_branch_id'      : branch_id,
        'default_store_id'       : store_id,
        'role_id'                : role_id,
        'is_default'             : True,
        'accessible_stores'      : {},
        'company_id'             : company_id,
        'branch_id'              : branch_id,
        're_created_at'          : dnow,
        're_created_by'          : getattr(user, 'id', None),
        're_updated_at'          : dnow,
        're_updated_by'          : getattr(user, 'id', None),
        'system_date'            : dnow.date(),
        'authorization'          : [
            {
                'id'      : getattr(user, 'id', None),
                'status'  : 'APPROVED',
                'datetime': str(dnow),
            }
        ],
        're_is_public'           : False,
    })

    db.add(ula_obj)
    db.flush()
    return ula_obj


@app.post("/token", response_model=Token)
async def login_for_access_token(
    request  : Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    lang     : str = "en",
    db       : Session = Depends(get_db),
):
    login_status, user, is_locked = authenticate_user(db, form_data.username, form_data.password)
    tokens = None
    if settings.KEYCLOAK_ENABLED == "true" :
        tokens = user.get("tokens") if isinstance(user, dict) else None

    if not login_status:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    dnow          = datetime.now()
    client_source = request.headers.get("X-Client-Source", "")

    # Keycloak login
    if tokens is not None:
        user_id     = user["id"]
        sid         = extract_sid_from_kc_token(tokens["access_token"])
        attributes  = fetch_kc_user_attributes(user_id)
        assignments = build_kc_assignments(attributes)
        context     = get_kc_default_context(user_id, db, attributes=attributes)

        if not context["accessible_company_id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no location assignment. Please contact the administrator.",
            )

        if assignments:
            sync_kc_ula(user_id, assignments, db, dnow)

        upsert_login_token(
            db                = db,
            user_id           = user_id,
            session_token     = sid,
            client_source     = client_source,
            user_agent        = request.headers.get("user-agent", ""),
            company_id        = context["accessible_company_id"],
            working_branch_id = context["default_branch_id"],
            working_store_id  = context.get("default_store_id"),
            accessible_stores = context.get("accessible_store"),
            expire_at         = dnow + timedelta(hours=8),
            dnow              = dnow,
        )
        db.commit()

        return {"access_token": tokens["access_token"], "token_type": "bearer"}

    # Local-DB login
    user_id = user.id

    ula_obj = ensure_default_user_location(db, user)

    tid                  = str(uuid.uuid4())
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token         = create_access_token(
        data={
            "sub": user_id,
            "tid": tid,
            "require_reset_password": bool(getattr(user, "require_reset_password", False)),
        },
        expires_delta=access_token_expires,
    )

    device = db.query(TBL_USER_LOGIN_TOKEN).filter(
        TBL_USER_LOGIN_TOKEN.user_id == user_id,
        TBL_USER_LOGIN_TOKEN.device.ilike('%mozilla%') if client_source != 'mobile'
        else ~TBL_USER_LOGIN_TOKEN.device.ilike('%mozilla%')
    ).first()

    if device:
        device.expire_at = str(dnow + access_token_expires)
        device.token     = tid
        db.commit()
    else:
        obj = TBL_USER_LOGIN_TOKEN(**{
            'user_id'           : user_id,
            'token'             : tid,
            'device'            : request.headers.get('user-agent', ''),
            're_created_at'     : dnow,
            'expire_at'         : str(dnow + access_token_expires),
            'company_id'        : ula_obj.accessible_company_id,
            'working_company_id': ula_obj.accessible_company_id,
            'working_branch_id' : ula_obj.default_branch_id,
            'working_store_id'  : ula_obj.default_store_id if ula_obj else '',
            're_is_public'      : False,
        })
        db.add(obj)
        db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "require_reset_password": bool(getattr(user, "require_reset_password", False)),
    }

@app.post("/api/v1/users/login", response_model=Token)
async def user_login_for_access_token(
    request  : Request,
    form_data: LoginPasswordSchema,
    db       : Session = Depends(get_db)
):
    login_status, user, is_locked = authenticate_user(db, form_data.username, form_data.password)
    tokens = user.get("tokens") if isinstance(user, dict) and settings.KEYCLOAK_ENABLED == "true" else None

    if not login_status:
        if is_locked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You have reached the maximum login attempt. Please try again later.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    is_kc_user = tokens is not None
    is_active  = user.get("enabled", True) if is_kc_user else user.is_active
    username   = user.get("username")      if is_kc_user else user.username
    user_id    = user.get("id")            if is_kc_user else user.id

    if not is_active:
        print(f"User '{username}' is inactive — blocking login.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive. Please contact the administrator.",
        )

    dnow          = datetime.now()
    client_source = request.headers.get('X-Client-Source', '')

    # Keycloak login
    if is_kc_user:
        _check_system_restriction(user_id)
        access_token_expires = timedelta(hours=8)

        sid         = extract_sid_from_kc_token(tokens["access_token"])
        attributes  = fetch_kc_user_attributes(user_id)
        assignments = build_kc_assignments(attributes)
        context     = get_kc_default_context(user_id, db, attributes=attributes)

        if not context["accessible_company_id"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User has no location assignment. Please contact the administrator.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if assignments:
            sync_kc_ula(user_id, assignments, db, dnow)
        else:
            # Auto-create default ULA if missing
            existing_ula = db.query(TBL_USER_LOCATION_ASSIGNMENT).filter(
                TBL_USER_LOCATION_ASSIGNMENT.user_id    == user_id,
                TBL_USER_LOCATION_ASSIGNMENT.is_default == True,
            ).first()

            if not existing_ula:
                db.add(TBL_USER_LOCATION_ASSIGNMENT(**{
                    "user_id"              : user_id,
                    "accessible_company_id": context["accessible_company_id"],
                    "default_branch_id"    : context["default_branch_id"],
                    "default_store_id"     : context.get("default_store_id", ""),
                    "accessible_stores"    : context.get("accessible_stores", []),
                    "is_default"           : True,
                    "created_at"           : dnow,
                }))

        db.query(TBL_USER_LOGIN_TOKEN).filter(
            TBL_USER_LOGIN_TOKEN.expire_at <= str(dnow)
        ).delete()

        upsert_login_token(
            db                   = db,
            user_id              = user_id,
            session_token        = sid,
            client_source        = client_source,
            user_agent           = request.headers.get("user-agent", ""),
            company_id           = context["accessible_company_id"],
            working_branch_id    = context["default_branch_id"],
            working_store_id     = context.get("default_store_id"),
            accessible_stores    = context.get("accessible_stores"),
            expire_at            = dnow + access_token_expires,
            dnow                 = dnow,
        )
        db.commit()

        return {
            "access_token" : tokens["access_token"],
            "token_type"   : "bearer",
            "refresh_token": tokens.get("refresh_token"),
        }
    
    # Local DB login — check 2FA before issuing token
    row = db.query(TBL_USER).filter(TBL_USER.id == user_id).first()
    if getattr(row, "two_factor", False):
        # Send OTP and return pending token instead of real token
        code       = "".join(random.choices(string.digits, k=6))
        expires_at = datetime.utcnow() + timedelta(minutes=CODE_TTL_MINUTES)
        email      = getattr(row, "email", None)

        existing = db.query(TBL_USER).filter(TBL_USER.id == user_id).first()
        if existing:
            existing.code = code; existing.expires_at = expires_at
        else:
            db.add(TBL_USER(id=user_id, code=code, expires_at=expires_at))
        db.commit()

        _send_otp_email_local(email, code)

        # Return short-lived pending token — NOT a real login token
        pending_token = create_access_token(
            data={"sub": user_id, "pending_2fa": True},
            expires_delta=timedelta(minutes=CODE_TTL_MINUTES),
        )
        return {
            "access_token" : pending_token,
            "token_type"   : "bearer",
            "pending_2fa"  : True,
            "message"      : "OTP sent to your email. Please verify to complete login.",
        }

    # Local DB login
    tid                  = str(uuid.uuid4())
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token         = create_access_token(
        data={
            "sub": user_id,
            "tid": tid,
            "require_reset_password": bool(getattr(user, "require_reset_password", False)),
        },
        expires_delta=access_token_expires,
    )

    ula_obj = ensure_default_user_location(db, user)

    db.query(TBL_USER_LOGIN_TOKEN).filter(
        TBL_USER_LOGIN_TOKEN.expire_at <= str(dnow)
    ).delete()


    device = db.query(TBL_USER_LOGIN_TOKEN).filter(
        TBL_USER_LOGIN_TOKEN.user_id == user_id,
        TBL_USER_LOGIN_TOKEN.device.ilike('%mozilla%') if client_source != 'mobile'
        else ~TBL_USER_LOGIN_TOKEN.device.ilike('%mozilla%')
    ).first()

    if device:
        device.expire_at = str(dnow + access_token_expires)
        device.token     = tid
        db.add(device)
    else:
        obj = TBL_USER_LOGIN_TOKEN(**{
            'user_id'           : user_id,
            'token'             : tid,
            'device'            : request.headers.get('user-agent', ''),
            're_created_at'     : dnow,
            'expire_at'         : str(dnow + access_token_expires),
            'company_id'        : ula_obj.accessible_company_id if ula_obj else '',
            'working_store_id'  : ula_obj.default_store_id,
            'working_company_id': ula_obj.accessible_company_id if ula_obj else '',
            'working_branch_id' : ula_obj.default_branch_id     if ula_obj else '',
        })
        db.add(obj)

    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "require_reset_password": bool(getattr(user, "require_reset_password", False)),
    }

@app.post("/api/v1/users/logout")
async def users_logout(
    request     : Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
    token       : Annotated[str, Depends(oauth2_scheme)],
    db          : Session = Depends(get_db),
):
    tid         = None
    is_keycloak = False

    try:
        # Local user — HS256 signed token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        tid     = payload.get("tid")
    except JWTError:
        #Keycloak token extract
        is_keycloak = True
        try:
            tid = extract_sid_from_kc_token(token)
        except Exception:
            tid = None

    # Clean up all expired tokens
    db.query(TBL_USER_LOGIN_TOKEN).filter(
        TBL_USER_LOGIN_TOKEN.expire_at <= str(datetime.now())
    ).delete(synchronize_session=False)

    # Delete this specific session
    if tid:
        db.query(TBL_USER_LOGIN_TOKEN).filter(
            TBL_USER_LOGIN_TOKEN.user_id == current_user.id,
            TBL_USER_LOGIN_TOKEN.token   == tid,
        ).delete(synchronize_session=False)

    # Release any record locks held by this user
    db.query(TBL_RECORD_LOCK).filter(
        TBL_RECORD_LOCK.locked_by  == current_user.id,
        TBL_RECORD_LOCK.company_id == current_user.token_working_company_id,
    ).delete(synchronize_session=False)

    db.commit()

    # Revoke Keycloak session (best-effort, never raises)
    if is_keycloak:
        revoke_kc_token(token)

    return {
        "status" : "success",
        "message": "Logout successfully",
        "data"   : jsonable_encoder(current_user),
    }

@app.post('/api/v1/users/cancel-record-lock')
def cancel_record_lock(
    current_user: Annotated[User, Depends(get_current_active_user)], 
    module_id   : str = Body(...), 
    db          : Session = Depends(get_db),
): 
    db.query(TBL_RECORD_LOCK).\
        filter(TBL_RECORD_LOCK.locked_by == current_user.id).\
        filter(TBL_RECORD_LOCK.module_id == module_id).\
        filter(TBL_RECORD_LOCK.company_id == current_user.token_working_company).\
        delete()
    db.commit()

    return {
        "status" : "success",
        "message": "Record lock canceled successfully",
        "data"   : jsonable_encoder(current_user)
    }

# @app.get("/v1/users/me/", response_model=User)
@app.get("/api/v1/users/me")
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
    lang        : str = "kh",
    db          : Session = Depends(get_db)
):
    # access_branches = current_user.access_branches.split(',')
    ab_query = db.query(TBL_USER_LOCATION_ASSIGNMENT).filter(TBL_USER_LOCATION_ASSIGNMENT.user_id==current_user.id, TBL_USER_LOCATION_ASSIGNMENT.accessible_company_id==current_user.token_working_company_id).all()
    access_branches = list(chain.from_iterable(
          x.accessible_branch_ids.split(',') for x in ab_query
      ))

    branches = db.query(TBL_BRANCH.id, TBL_BRANCH.name).filter(TBL_BRANCH.id.in_(access_branches)).all()
    roleObj = db.query(TBL_USER_LOCATION_ASSIGNMENT.id, TBL_ROLE.name,TBL_ROLE.is_superuser).\
        join(TBL_ROLE, TBL_USER_LOCATION_ASSIGNMENT.role_id==TBL_ROLE.id).\
        filter(TBL_USER_LOCATION_ASSIGNMENT.user_id==current_user.id).all()
        
    user_log_token = db.query(TBL_USER_LOGIN_TOKEN). \
        filter(TBL_USER_LOGIN_TOKEN.user_id == current_user.id). \
        order_by(TBL_USER_LOGIN_TOKEN.re_created_at.desc()). \
        first()
        

    employee = None
    department = None
    division = None
    user_position = None
    company_name = db.query(TBL_COMPANY.name).filter(TBL_COMPANY.id==current_user.token_working_company_id).first()
    branch_name = db.query(TBL_BRANCH.name).filter(TBL_BRANCH.id==current_user.token_working_branch_id).first()
        
    role = ''
    is_superuser = False
    for r in roleObj:
        role = r.name
        if r.is_superuser:
            is_superuser = True
            break
        
    data = {
        'id'             : current_user.id,
        'username'       : current_user.username,
        'email'          : current_user.email,
        'phone'          : current_user.phone,
        'first_name'     : current_user.first_name,
        'last_name'      : current_user.last_name,
        # 'date_of_birth'  : current_user.date_of_birth,
        # 'full_name'      : current_user.full_name,
        'photo'          : current_user.photo,
        'photo_link'     : f"{os.getenv('APP_URL','')}/static/images/User/{current_user.photo}" if current_user.photo else None,
        # 'gender'         : current_user.gender,
        'language'       : current_user.language,
        'is_superuser'   : is_superuser,
        'role'           : role,
        'roles'          : [
            {
                'id'          : r.id,
                'name'        : r.name,
                'is_superuser': r.is_superuser,
            } for r in roleObj
        ],
        'access_branches': [
            {
                'id'  : b.id,
                'name': b.name,
            } for b in branches
        ],
        'working_branch_id' : current_user.token_working_branch_id,
        'working_company_id': current_user.token_working_company_id,
        'working_branch_name': branch_name.name if branch_name else '',
        'working_company_name': company_name.name if company_name else '',
        'log_time'       : user_log_token.re_created_at.strftime('%Y-%m-%d %H:%M:%S') if user_log_token else "",
        'company_id'     : current_user.company_id,
        'department_id'  : getattr(department, 'id', '') if department else "",
        'department_name'     : getattr(department, 'name', '') if department else "",
        'department_name_lc'  : getattr(department, 'name_lc', '') if department else "",
        'division_id'  : getattr(division, 'id', '') if division else "",
        'division_name'     : getattr(division, 'name', '') if division else "",
        'division_name_lc'  : getattr(division, 'name_lc', '') if division else "",
    }
    return JSONResponse({
        'ok'        : True,
        'status'    : 200,
        'title'     : 'User',
        "message"   : 'User data retrieved successfully',
        "error"     : {},
        'data'      : jsonable_encoder(data),
        "request_id": app.state.request_id
    }, status_code = 200)

@app.get('/get-user-permissions')
def get_user_permissions(
    current_user    : Annotated[User, Depends(get_current_active_user)],
    db              : Session = Depends(get_db)
): 
    data = []
    if core_lib.check_is_superuser(db, current_user): 
        m_query = db.query(TBL_MODULE.id, TBL_MODULE.name, TBL_ROLE_MODULE.permission).\
            outerjoin(TBL_ROLE_MODULE, TBL_ROLE_MODULE.module_id == TBL_MODULE.id).\
            all()

        data = [
            {
                'id'        : m.id,
                'name'      : m.name,
                'permission': 'VL,VH,VU,VD,VR,LL,LH,LU,LD,LR,C,U,D,A,R,P,EP'
            }
            for m in m_query
        ]

    else:
        role_ids = get_effective_role_ids(db, current_user)

        m_query = db.query(TBL_MODULE.id, TBL_MODULE.name, TBL_ROLE_MODULE.permission).\
            outerjoin(TBL_ROLE_MODULE, TBL_ROLE_MODULE.module_id == TBL_MODULE.id).\
            outerjoin(TBL_ROLE, TBL_ROLE.id == TBL_ROLE_MODULE.parent_id).\
            filter(TBL_ROLE.id.in_(role_ids)).\
            filter(TBL_ROLE.company_id == current_user.token_working_company_id).\
            filter(TBL_ROLE_MODULE.company_id == current_user.token_working_company_id).\
            all() if role_ids else []

        data = [
            {
                'id'        : m.id,
                'name'      : m.name,
                'permission': ','.join(m.permission.split(' ')) if m.permission else ''
            }
            for m in m_query
        ]

        data.extend([
            {
                'id'        : m.id,
                'name'      : m.name,
                'permission': ','.join(m.permission.replace(',', ' ').split()) if m.permission else ''
            }
            for m in get_active_delegated_permission_rows(db, current_user)
        ])
            

    return ResponseModel(
        ok        = True,
        status    = 200,
        title     = 'Permission',
        message   = 'Permission data retrieved successfully',
        data      = data
    )

@app.get("/generate-qr")
def generate_qr(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    branch = db.query(TBL_BRANCH).filter(TBL_BRANCH.id == current_user.token_working_branch_id).first()

    data = {
        'app_name': 'TalentEdge',
        'company_id': current_user.token_working_company_id,
        'latlong': getattr(branch, 'lat_long', None),
    }
    data_str = json.dumps(data)  

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data_str)  
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")


@app.post("/api/v1/users/set-language")
async def set_user_language(
    data:UserChangeLanguageSchema,
    current_user: Annotated[User, Depends(get_current_active_user)], lang: str = "kh",
    db: Session = Depends(get_db),
):
    current_user.language = data.lang
    db.add(current_user)
    db.commit()
   
    return JSONResponse({
        'ok': True,
        'status': 200,
        'title': 'User',
        "message": 'User set language successfully',
        "error": {},
        'data': {},
        # "redirect_url": "",
        "request_id": app.state.request_id
    }, status_code = 200)


"""
User change password.

Parameters:
old_password (str): The old password.
new_password (str): The new password.
new_password_confirm (str): The new password confirm.

Returns:
object
"""
@app.post("/api/v1/users/change-password")
async def user_change_password(data:UserChangePasswordSchema,
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    if not verify_password(data.old_password, current_user.password):
        raise HTTPException(
            status_code=422,
            detail="Incorrect password"
        )
    if not check_valid_password(data.new_password):
        raise HTTPException(
            status_code=422,
            detail="Password is not strong. It must contain number, symbols, lowercase and uppercase letter"
        )

    if data.new_password != data.new_password_confirm:
        raise HTTPException(
            status_code=422,
            detail="Confirm password is not matched"
        )

    current_user.password = get_password_hash(data.new_password)
    current_user.require_reset_password = False
    db.add(current_user)
    db.commit()

    return {'message':'Password change successfully'}

@app.post("/api/v1/users/reset-pin")
async def user_reset_pin(data:UserResetPINSchema,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db          : Session = Depends(get_db)
):
    if not verify_password(data.old_pin, current_user.pin):
        raise HTTPException(
            status_code=422,
            detail="Incorrect PIN"
        )
    if not check_valid_pin(data.new_pin):
        raise HTTPException(
            status_code=422,
            detail="PIN is not correct. Its lenght must be 6 digits"
        )

    if data.new_pin != data.new_pin_confirm:
        raise HTTPException(
            status_code=422,
            detail="Confirm PIN is not matched"
        )

    current_user.pin = get_password_hash(data.new_pin)
    db.add(current_user)
    db.commit()

    return {'message':'PIN reset successfully'}


@app.post("/api/v1/users/set-pin")
async def user_set_pin(data:UserSetPINSchema,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db          : Session = Depends(get_db)
):
    
    if not check_valid_pin(data.new_pin):
        raise HTTPException(
            status_code=422,
            detail="PIN is not correct. Its lenght must be 6 digits"
        )

    if data.new_pin != data.new_pin_confirm:
        raise HTTPException(
            status_code=422,
            detail="Confirm PIN is not matched"
        )

    current_user.pin = get_password_hash(data.new_pin)
    db.add(current_user)
    db.commit()

    return {'message':'PIN reset successfully'}

@app.post("/api/v1/users/switch-branch")
async def user_switch_branch(
    request     : Request, 
    data        : BranchIdSchema,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db          : Session = Depends(get_db),
):
    ab_query = db.query(TBL_USER_LOCATION_ASSIGNMENT).filter(
        TBL_USER_LOCATION_ASSIGNMENT.user_id==current_user.id, 
        TBL_USER_LOCATION_ASSIGNMENT.accessible_company_id==current_user.token_working_company_id
    ).all()
    access_branches = list(chain.from_iterable(
          x.accessible_branch_ids.split(',') for x in ab_query
      ))

    if check_is_superuser(db, current_user):
        b_query = db.query(TBL_BRANCH).filter(TBL_BRANCH.company_id==current_user.token_working_company_id).all()
        access_branches = [x.id for x in b_query]
    
    client_source = request.headers.get('X-Client-Source', '')

    filter = [TBL_USER_LOGIN_TOKEN.user_id == current_user.id]
    
    if client_source == 'mobile': 
        filter.append(~TBL_USER_LOGIN_TOKEN.device.ilike('%mozilla%'))
    
    if client_source == 'web': 
        filter.append(TBL_USER_LOGIN_TOKEN.device.ilike('%mozilla%'))

    ult_query = db.query(TBL_USER_LOGIN_TOKEN).filter(*filter).first()

    if not ult_query:
        raise HTTPException(
            status_code=422,
            detail="User is not logged in"
        )
    
    if not data.branch_id in access_branches:
        raise HTTPException(
            status_code=422,
            detail="Cannot switch to this branch. You do not have access to this branch"
        )
    
    ult_query.working_branch_id = data.branch_id
    ula_obj = db.query(TBL_USER_LOCATION_ASSIGNMENT).filter(
        TBL_USER_LOCATION_ASSIGNMENT.user_id == current_user.id,
        TBL_USER_LOCATION_ASSIGNMENT.accessible_company_id == current_user.token_working_company_id,
    ).first()
    
    if ula_obj and data.branch_id in ula_obj.accessible_branch_ids.split(','):
        ult_query.working_store_id = ula_obj.accessible_stores.get(data.branch_id, {}).get('default_store_id', 'HS')

    db.commit()

    return {'message':'Branch switch successfully'}

@app.post("/api/v1/users/switch-company")
async def user_switch_branch(
    request     : Request,
    data        : CompanyIdSchema,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db          : Session = Depends(get_db)
):
    query = db.query(TBL_USER_LOCATION_ASSIGNMENT).filter(TBL_USER_LOCATION_ASSIGNMENT.user_id == current_user.id).all()
    access_companies = [x.accessible_company_id for x in query]

    client_source = request.headers.get('X-Client-Source', '')

    filter = [TBL_USER_LOGIN_TOKEN.user_id == current_user.id]
    
    if client_source == 'mobile': 
        filter.append(~TBL_USER_LOGIN_TOKEN.device.ilike('%mozilla%'))
    
    if client_source == 'web': 
        filter.append(TBL_USER_LOGIN_TOKEN.device.ilike('%mozilla%'))

    ult_query = db.query(TBL_USER_LOGIN_TOKEN).filter(*filter).first()

    if not ult_query:
        raise HTTPException(
            status_code=422,
            detail="User is not logged in"
        )
    
    if not data.company_id in access_companies and not core_lib.check_is_superuser(db, current_user):
        raise HTTPException(
            status_code=422,
            detail="Cannot switch to this company. You do not have access to this company"
        )
    
    default_branch_id = db.query(TBL_USER_LOCATION_ASSIGNMENT).\
    filter(TBL_USER_LOCATION_ASSIGNMENT.accessible_company_id == data.company_id).first()

    ult_query.working_company_id = data.company_id
    ult_query.working_branch_id = getattr(default_branch_id, 'default_branch_id', 'HQ')
    ult_query.working_store_id = getattr(default_branch_id, 'default_store_id', 'HS')
    db.commit()

    return {'message':'Company switch successfully'}

@app.get("/api/v1/users/get-list-access-branches")
async def user_get_list_access_branches(
    current_user        : Annotated[User, Depends(get_current_active_user)],
    page                : int = Query(default=1, ge=1),
    size                : int = Query(default=10, ge=1),
    search              : str = Query(default=''),   
    lang                : str = 'en',
    db                  : Session = Depends(get_db),
    ):
    ab_query = db.query(TBL_USER_LOCATION_ASSIGNMENT).filter(
        TBL_USER_LOCATION_ASSIGNMENT.user_id==current_user.id, 
        TBL_USER_LOCATION_ASSIGNMENT.accessible_company_id==current_user.token_working_company_id,
        )
    
    total = ab_query.count()

    # Apply pagination
    result = ab_query.offset((page - 1) * size).limit(size).all()

    total_pages = max(math.ceil(total / size), 1)

    access_branches = list(chain.from_iterable(
          x.accessible_branch_ids.split(',') for x in result
      ))
    
    lang_filter = [
        TBL_BRANCH.name.ilike(f"%{search}%")
        if lang == 'en'
        else TBL_BRANCH.name_lc.ilike(f"%{search}%")
    ]
    
    branches = db.query(
        TBL_BRANCH.id, TBL_BRANCH.name, 
        TBL_BRANCH.comment, TBL_BRANCH.image, 
        TBL_BRANCH.company_id, TBL_BRANCH.phone, 
        TBL_BRANCH.email
        ).\
        filter(*lang_filter)
    
    if not core_lib.check_is_superuser(db, current_user): 
        branches = branches.filter(TBL_BRANCH.id.in_(access_branches)).all()
    else: 
        branches = branches.filter(TBL_BRANCH.company_id==current_user.token_working_company_id).all()


    data = []

    for b in branches: 
        branches_data = {
            'id'           : getattr(b, 'id', None),
            'name'         : getattr(b, 'name', None),
            'comment'      : getattr(b, 'comment', None),
            'phone'        : getattr(b, 'phone', None),
            'email'        : getattr(b, 'email', None),
            'company_id'   : getattr(b, 'company_id', None),
            'image'        : getattr(b, 'image', None),
            'image_link'   : f"{os.getenv('APP_URL','')}/static/images/Branch/" + getattr(b, 'image', None),
        }
        data.append(branches_data)

    return response_msg(
        title  = 'List Accessible Branches',
        msg    = 'Access branch data retrieved successfully',
        code   = 200,
        status = True,
        error  = {},
        data   = {
            'list'     : jsonable_encoder(data),
            "meta_data": {
                'total'       : total,
                'total_page'  : total_pages,
                'current_page': page,
                'size'        : size,
            },
        }
    )

@app.get("/api/v1/users/get-list-access-company")
async def user_get_list_access_branches(
    current_user    : Annotated[User, Depends(get_current_active_user)],
    page            : int = Query(default=1, ge=1),
    size            : int = Query(default=10, ge=1),
    search          : str = Query(default=''),
    lang            : str = 'en',
    db              : Session = Depends(get_db),
):
    query = db.query(TBL_USER_LOCATION_ASSIGNMENT).filter(TBL_USER_LOCATION_ASSIGNMENT.user_id == current_user.id).all()
    access_companies = [x.accessible_company_id for x in query]
    companies = db.query(
        TBL_COMPANY.id, 
        TBL_COMPANY.name, 
        TBL_COMPANY.description, 
        TBL_COMPANY.logo, 
        TBL_COMPANY.company_id, 
        TBL_COMPANY.phone, 
        TBL_COMPANY.email,
    )
    
    if not core_lib.check_is_superuser(db, current_user): 
        companies = companies.filter(TBL_COMPANY.id.in_(access_companies))

    total = companies.count()

    lang_filter = [
        TBL_COMPANY.name.ilike(f"%{search}%")
        if lang == 'en'
        else TBL_COMPANY.name_lc.ilike(f"%{search}%")
    ]

    # Apply pagination
    result = companies.filter(*lang_filter).offset((page - 1) * size).limit(size).all()

    data = []

    for c in result: 
        data.append({
            'id'         : getattr(c, 'id', None),
            'name'       : getattr(c, 'name', None),
            'description': getattr(c, 'description', None),
            'phone'      : getattr(c, 'phone', None),
            'email'      : getattr(c, 'email', None),
            'company_id' : getattr(c, 'company_id', None),
            'logo'       : getattr(c, 'logo', None),
            'logo_link'  : f"{os.getenv('APP_URL','')}/static/images/Company/" + getattr(c, 'logo', None),
        })

    total_pages = max(math.ceil(total / size), 1)

    return response_msg(
        title  = 'List Accessible Companies',
        msg    = 'Access company data retrieved successfully',
        code   = 200,
        status = True,
        error  = {},
        data   = {
            'list'     : data,
            "meta_data": {
                'total'       : total,
                'total_page'  : total_pages,
                'current_page': page,
                'size'        : size,
            },
        }
    )




@app.get("/api/v1/users/unauthorized-request")
async def unauthorized_request(current_user: Annotated[User, Depends(get_current_active_user)]):
    query = text(f"""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name LIKE '%unauth';
            """)
    result = db.execute(query)
    tables = [row[0] for row in result.fetchall()]
    
    tables_with_records = []
    for table in tables:
        result = db.execute(text(f"SELECT EXISTS (SELECT 1 FROM {table} LIMIT 1)"))
        has_records = result.scalar()
        if has_records:
            print(table)
            tables_with_records.append(table)
    return {'message':tables_with_records}


@app.get("/api/v1/wb/get-user-access-branches/query-list")
async def user_get_list_access_branches(
    current_user: Annotated[User, Depends(get_current_active_user)],
    search      : str = '',                                            # [{"field":"name","value":"an"},{"field":"name","value":"an"}]
    page        : int = 1,
    size        : int = 10,
    show_all    : bool = False,
    lang        : str = 'en',
    db          : Session = Depends(get_db)
    ):
    '''
      List data with pagination\n
      Data Format:\n
      search: [{"field":"name","value":"an"},{"field":"name","value":"an"}]
      '''
    try:
        access_branches = current_user.access_branches.split(',')
        query = db.query(
            TBL_BRANCH.id,
            TBL_BRANCH.name,
            TBL_BRANCH.name_lc,
            TBL_BRANCH.phone,
            TBL_BRANCH.email
        ).filter(TBL_BRANCH.id.in_(access_branches))

        # Filter
        if search:
            search_filters = []
            for item in json.loads(search):
                field = item.get("field")
                value = item.get("value")
                if field and value:
                    search_filters.append(getattr(TBL_BRANCH, field).ilike(f"%{value}%"))
                    
            if search_filters:
                query = query.filter(or_(*search_filters))

        total_records = query.count()

        if not show_all:
            offset = (page - 1) * size
            query = query.offset(offset).limit(size)

        branches = query.all()

        return render_detail(
            status=True,
            title='User Access branch',
            module='lists',
            message='Data retrieved successfully',
            data=jsonable_encoder(branches),
            total_record=total_records,
            offset=offset,
            limit=size if not show_all else total_records,
        )
    except Exception as e:
        return render_detail(
            status=False,
            title='User Access branch',
            module='lists',
            message=str(e),
            data=[],
            total_record=0,
            offset=0,
            limit=1,
        )

@app.get("/api/v1/users/dashboard-cards")
async def get_user_dashboard_cards(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db          : Session = Depends(get_db)
):
    """
    Retrieve the dashboard cards for the current active user.
    This endpoint fetches the dashboard cards associated with the current active user
    by querying the database and joining the necessary tables.
    Args:
        current_user (User): The current active user obtained from the dependency injection.
    Returns:
        dict: A dictionary containing the status, title, message, module, and the retrieved data.
    """
    dashboards = db.query(
        TBL_DASHBOARD_ITEM.id,
        TBL_DASHBOARD_ITEM.name,
        TBL_DASHBOARD_ITEM.dashboard_card,
        TBL_DASHBOARD_ITEM.order,
        TBL_DASHBOARD_ITEM.width).\
        join(TBL_DASHBOARDS, TBL_DASHBOARDS.id==TBL_DASHBOARD_ITEM.parent_id).\
        join(TBL_USER, TBL_USER.dashboard_id==TBL_DASHBOARDS.id).\
        filter(TBL_USER.id==current_user.id).all()
        
    return_data = dict(
        status       = True,
        title        = 'User',
        message      = 'Data was retrieved successfully',
        module       = 'User',
        data         = jsonable_encoder(dashboards),
    )
    
    return return_data

if settings.KEYCLOAK_ENABLED == "true":
    class USER_KEYCLOAK_CRUD_API(KeycloakCRUDAPI):

        def get_header(self):
            return []
    
        def _format_user(self, user: dict) -> dict:
            roles      = user.get("roles", [])
            first_role = roles[0] if roles else {}
    
            return {
                "user_id"    : user.get("user_id") or user.get("id"),
                "username"   : user.get("username"),
                "email"      : user.get("email"),
                "enabled"    : user.get("enabled"),
                "given_name" : user.get("first_name"),
                "family_name": user.get("last_name"),
                "age"        : user.get("age"),
                "phone"      : user.get("phone"),
                "dob"        : user.get("dob"), 
                "roles": [
                    {
                        "accessible_company_id": r.get("accessible_company_id"),
                        "accessible_branch_ids": r.get("accessible_branch_ids"),
                        "default_branch_id"    : r.get("default_branch_id"),
                        "default_store_id"     : r.get("default_store_id"),
                        "accessible_stores"    : r.get("accessible_stores") or {},
                        "role_id"              : r.get("role_id"),
                        "is_default"           : r.get("is_default"),
                    }
                    for r in roles
                ],
            }
    
        def before_view_response(self, data):
            return self._format_user(data)
    
        def before_list_response(self, data):
            data["users"] = [self._format_user(u) for u in data.get("users", [])]
            return data

        def before_save(self):
            domain = self.item.get("email", "").split("@")[-1]
            if domain in {"mailinator.com", "tempmail.com"}:
                return False, "Disposable email addresses are not allowed"
            return True, ""

        def before_update(self):
            if self.item.get("enabled") is False and self.user_id == self.current_user.id:
                return False, "You cannot disable your own account"
            return True, ""

        def before_delete(self):
            if self.user_id == self.current_user.id:
                return False, "You cannot delete your own account"
            return True, ""

        def before_forgot_otp(self, body, db):
            OTPModel     = self._require_otp_model()
            access_token = _get_admin_token()
            user         = _find_user_by_username(access_token, _field(body, "username"))
            user_id      = user["id"]
            _verify_email_matches(user, _field(body, "email", ""))
            display_name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
            code         = _generate_code()
            expires_at   = datetime.utcnow() + timedelta(minutes=CODE_TTL_MINUTES)

            existing = db.query(OTPModel).filter(OTPModel.id == user_id).first()
            if existing:
                existing.code       = code
                existing.expires_at = expires_at
            else:
                db.add(OTPModel(id=user_id, code=code, expires_at=expires_at))
            db.commit()

            _send_otp_email(access_token, _field(body, "email"), code, display_name)
            return _ok(self.module, "A 6-digit reset code has been sent to your email.")

        def before_verify_code(self, body, db):
            OTPModel     = self._require_otp_model()
            access_token = _get_admin_token()
            user         = _find_user_by_username(access_token, _field(body, "username"))

            record = db.query(OTPModel).filter(
                OTPModel.id        == user["id"],
                OTPModel.code      == _field(body, "code"),
                OTPModel.expires_at > datetime.utcnow(),
            ).first()
            if not record:
                raise HTTPException(status_code=400, detail="Invalid or expired reset code.")
            return _ok(self.module, "Code verified. You may now set a new password.")

        def before_confirm_reset(self, body, db):
            OTPModel     = self._require_otp_model()
            access_token = _get_admin_token()
            user         = _find_user_by_username(access_token, _field(body, "username"))
            user_id      = user["id"]

            record = db.query(OTPModel).filter(
                OTPModel.id        == user_id,
                OTPModel.code      == _field(body, "code"),
                OTPModel.expires_at > datetime.utcnow(),
            ).first()
            if not record:
                raise HTTPException(status_code=400, detail="Invalid or expired reset code.")

            _keycloak_set_password(user_id, _field(body, "new_password"), temporary=False)
            user_row = db.query(TBL_USER).filter(TBL_USER.id == user_id).first()
            if user_row and hasattr(user_row, "require_reset_password"):
                user_row.require_reset_password = False
                db.add(user_row)
            db.delete(record)
            db.commit()
            return _ok(self.module, "Password has been reset successfully.")


    crud = USER_KEYCLOAK_CRUD_API(
        'KeyCloakUser',
        'keycloak/users',
        {},
        schema               = UserSchema,
        update_schema        = KCUserUpdateSchema,
        register_schema      = UserRegisterSchema,
        forgot_link_schema   = KCForgotPasswordLinkRequest,
        forgot_otp_schema    = KCForgotPasswordOTPRequest,
        verify_code_schema   = KCVerifyResetCodeRequest,
        confirm_reset_schema = KCConfirmResetPasswordRequest,
        admin_reset_schema   = KCResetPasswordRequest,
        otp_model            = TBL_USER,  
    )
    crud.init_route()
    app.include_router(crud.router, prefix="/api/v1", tags=["User KeyCloak"])
