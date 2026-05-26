import time, uuid, os, ast, re
import logging
from fastapi import Body
from fastapi.encoders import jsonable_encoder
from icb.api.branch.models import TBL_BRANCH
from icb.api.system_date.models import TBL_SYSTEM_DATE
from icb.core.db_session import get_db
from sqlalchemy import or_
from sqlalchemy.orm import Session
from icb.lib.render_api import response_msg
from icb.lib.utils import get_case_expr
from icb.core.crud_api import *
from icb.api.user.models import TBL_USER
from icb.api.role.models import TBL_ROLE, TBL_ROLE_MODULE
from icb.core.role_delegation import get_active_delegated_module_ids, get_effective_role_ids
from icb.api.menu.models import *
from .schemas import *
from main import app
from sqlalchemy import func
import icb.core.lib as core_lib
___ = core_lib.get_lang

logger = logging.getLogger(__name__)

class MENU_CRUD_API(CRUDAPI):
    query_fields = ['name']

    def get_header(self):
        return [
            {"field": "id", "text": "ID"},
            {"field": "description", "text": "Description"},
            {"field": "ordering", "text": "Ordering"},
        ]

    def get_header_sub(self):
        return {
            'sub_menu': [
                {"field": "id", "text": "ID"},
                {"field": "main_id", "text": "Main ID"},
                {"field": "label", "text": "Label"},
                {"field": "type", "text": "Type"},
                {"field": "url", "text": "URL"},
                {"field": "icon", "text": "Icon"},
                {"field": "module_id", "text": "Module ID"},
                {"field": "name", "model": TBL_MODULE, "label": "module_name", "text": "Module Name"},
            ]
        }

    # get_vsi_query used a bare global `db` — it must receive db as a parameter
    def get_vsi_query(self, db: Session, record_type=''):
        model = getattr(self.moduleList, str(self.sub_models.get('sub_menu').__name__) + record_type)
        query = db.query(model).outerjoin(TBL_MODULE, TBL_MODULE.id == model.module_id)
        return {'sub_menu': query}


crud = MENU_CRUD_API('Menu', 'menus', TBL_MENU,
    {'sub_menu': TBL_SUB_MENU},
    schema=MenuSchema,
    sub_schema=SubMenuListSchema
)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Menu'])


class MENU_ITEM_CRUD_API(CRUDAPI):
    query_fields = ['name']

    def get_header(self):
        return [
            {"field": "id", "text": "ID"},
            {"field": "type", "text": "Type"},
            {"field": "label", "text": "Label"},
            {"field": "module_id", "text": "Module ID"},
            {"field": "name", "model": TBL_MODULE, "label": "module_name", "text": "Module Name"},
            {"field": "url", "text": "URL"},
            {"field": "icon", "text": "Icon"},
        ]

    def get_list_query(self, model):
        return self.db.query(model).outerjoin(TBL_MODULE, TBL_MODULE.id == model.module_id)


crud = MENU_ITEM_CRUD_API('MenuItem', 'menu-items', TBL_MENU_ITEM, {}, schema=MenuItemSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Menu Item'])


@app.get("/api/v1/wb/get-menu-setup-list", tags=['Menu'])
async def get_menu_list_item(
    current_user: Annotated[User, Depends(get_current_active_user)],
    menu_id     : str = "1",
    lang        : str = "kh",
    db          : Session = Depends(get_db)
):
    return get_menu_for_render(menu_id, current_user, db, lang)


@app.get("/api/v1/get-menu-list-view", tags=['Menu'])
async def get_menu_list_view(
    current_user: Annotated[User, Depends(get_current_active_user)],
    menu_id     : str = "1",
    lang        : str = "kh",
    db          : Session = Depends(get_db)
):
    return get_menu_for_render(menu_id, current_user, db, lang, list_permission_type=True)


def get_menu_for_render(menu_id, current_user, db: Session, lang='en', list_permission_type=False):
    menus = db.query(TBL_SUB_MENU).\
        filter(TBL_SUB_MENU.parent_id == menu_id).\
        filter(or_(TBL_SUB_MENU.main_id.is_(None), TBL_SUB_MENU.main_id == '')).\
        order_by(TBL_SUB_MENU.ordering).all()

    def fetch_sub_menus(parent_id, menu_id):
        return db.query(
                TBL_SUB_MENU.id,
                TBL_MENU_ITEM.label,
                TBL_MENU_ITEM.icon,
                TBL_MENU_ITEM.type,
                TBL_MENU_ITEM.module_id,
                TBL_MENU_ITEM.url,
            ).\
            outerjoin(TBL_MENU_ITEM, TBL_MENU_ITEM.id == TBL_SUB_MENU.id).\
            filter(TBL_SUB_MENU.main_id == str(parent_id)).\
            filter(TBL_SUB_MENU.parent_id == str(menu_id)).\
            order_by(TBL_SUB_MENU.ordering).all()

    def get_list_sub_menu(parent_id, menu_id, role_modules=[], user_role=None, list_permission_type=False):
        menu_list = []
        sub_menus = fetch_sub_menus(parent_id, menu_id)
        if sub_menus:
            for sub_menu in sub_menus:
                if not list_permission_type and str(sub_menu.type).lower() == 'permission':
                    continue

                menus    = fetch_sub_menus(sub_menu.id, menu_id)
                sub_item = get_list_sub_menu(sub_menu.id, menu_id, role_modules, user_role, list_permission_type) if menus else []
                if not (user_role and user_role.is_superuser):
                    if str(sub_menu.type).lower() == 'standard' and (not sub_menu.module_id in role_modules):
                        continue
                    if str(sub_menu.type).lower() != 'standard' and (not sub_item):
                        continue

                menu_list.append({
                    "id"          : sub_menu.id,
                    "title"       : sub_menu.label,
                    "icon"        : sub_menu.icon,
                    "type"        : sub_menu.type,
                    "url"         : sub_menu.url,
                    "module_id"   : sub_menu.module_id,
                    "badgeContent": "",
                    "badgeColor"  : "",
                    "children"    : sub_item
                })

        return menu_list

    menu_list = []
    user_role = get_current_role(current_user, db)
    role_modules = get_role_modules(current_user, db)
    menu_types = ['standard', 'permission'] if list_permission_type else ['standard']
    for menu in menus:
        child_menu = get_list_sub_menu(menu.id, menu_id, role_modules, user_role, list_permission_type)
        if child_menu or (menu.type.lower() in menu_types and (user_role and (user_role.is_superuser or menu.module_id in role_modules))):
            menu_list.append({
                "id"          : menu.id,
                "title"       : menu.label,
                "icon"        : menu.icon,
                "type"        : menu.type,
                "url"         : menu.url,
                "module_id"   : menu.module_id,
                "badgeContent": "",
                "badgeColor"  : "",
                "children"    : child_menu
            })

    return menu_list


def get_current_role(current_user, db: Session):
    role_ids = get_effective_role_ids(db, current_user)
    if not role_ids:
        return None

    return db.query(TBL_ROLE).\
        filter(TBL_ROLE.id.in_(role_ids)).\
        filter(TBL_ROLE.company_id == current_user.token_working_company_id).\
        order_by(TBL_ROLE.is_superuser.desc()).\
        first()


def get_role_modules(current_user, db: Session):
    user_role = get_current_role(current_user, db)

    if user_role and user_role.is_superuser:
        return [str(id) for id, in db.query(TBL_MODULE.id).distinct().all()]

    role_ids = get_effective_role_ids(db, current_user)
    if not role_ids:
        return get_active_delegated_module_ids(db, current_user)

    user_roles = db.query(TBL_ROLE_MODULE.module_id) \
        .join(TBL_ROLE, TBL_ROLE.id == TBL_ROLE_MODULE.parent_id) \
        .filter(TBL_ROLE_MODULE.parent_id.in_(role_ids),
                TBL_ROLE.company_id == current_user.token_working_company_id,
                TBL_ROLE_MODULE.company_id == current_user.token_working_company_id,
                TBL_ROLE_MODULE.permission != '',
                TBL_ROLE_MODULE.permission != None).all()

    module_ids = [module_id for module_id, in user_roles]
    module_ids.extend(get_active_delegated_module_ids(db, current_user))

    return list(dict.fromkeys(module_ids))


@app.get("/api/v1/get-menu-setup-list", tags=['Menu'])
async def get_menu_setup_list(
    current_user: Annotated[User, Depends(get_current_active_user)],
    lang: str = "kh",
    db: Session = Depends(get_db)
):
    menu_id = "1"
    return get_menu_for_render(menu_id, current_user, db, lang)


@app.post("/api/v1/wb/save-menu-setup", tags=['Menu'])
async def save_menu_setup(
    item        : Annotated[MenuSchema, Body(embed=True)],
    sub_item    : SubMenuListSchema,
    current_user: Annotated[User, Depends(get_current_active_user)],
    lang        : str = "kh",
):
    db_session = None
    try:
        db_session = next(get_db())

        moduleList = __import__("main")
        model = TBL_MENU
        sub_models = {'sub_menu': TBL_SUB_MENU}
        item_dict = item.dict()
        schema = MenuSchema
        sub_item_dict = sub_item.dict() if sub_item else None

        menu_id = item_dict.get('id') or core_lib.get_module_id('Menu')

        existing_obj = db_session.query(model).filter(model.id == menu_id).first()
        if existing_obj:
            return {
                'ok': False,
                'status': 400,
                'title': ___('notice', {}, lang),
                'message': ___('record_id_already_exist', {}, lang),
                'error': {'id': ___('record_id_already_exist', {}, lang)},
                'data': {}
            }

        modelDel = getattr(moduleList, str(model.__name__) + "_DELETED", None)
        if modelDel:
            deleted_obj = db_session.query(modelDel).filter(modelDel.id == menu_id).first()
            if deleted_obj:
                return {
                    'ok': False,
                    'status': 400,
                    'title': ___('notice', {}, lang),
                    'message': ___('record_id_already_exist', {}, lang),
                    'error': {'id': ___('record_id_already_exist', {}, lang)},
                    'data': {}
                }

        validation_data = dict(item_dict)
        validation_data.update({
            'is_manual_validation': True,
            'id': menu_id,
            'lang': lang,
            'current_user': jsonable_encoder(current_user)
        })

        schema(**validation_data)

        auth_data = [{
            'id': current_user.id,
            'status': 'APPROVED',
            'datetime': str(core_lib.get_datetime_now())
        }]

        system_date_obj = db_session.query(TBL_SYSTEM_DATE).first()

        base_dict = {
            'id': menu_id,
            're_version': 0,
            'authorization': auth_data,
            're_status': 'AUTH',
            're_created_by': current_user.id,
            're_created_at': str(core_lib.get_datetime_now()),
            're_updated_by': current_user.id,
            're_updated_at': str(core_lib.get_datetime_now()),
            'system_date': system_date_obj.current_system_date if system_date_obj else None,
            'branch_id': current_user.token_working_branch_id,
            'company_id': current_user.token_working_company_id
        }

        item_dict.update(base_dict)
        menu_obj = model(**item_dict)
        db_session.add(menu_obj)

        if sub_item_dict:
            for sub_item_key, list_sub_items in sub_item_dict.items():
                if sub_item_key in sub_models and list_sub_items:
                    sub_model = sub_models[sub_item_key]
                    for sub_item_data in list_sub_items:
                        sub_id = sub_item_data.get('id', '')
                        sub_item_data.update(base_dict)
                        sub_item_data.update({
                            'parent_id': menu_id,
                            'id': sub_id
                        })
                        sub_obj = sub_model(**sub_item_data)
                        db_session.add(sub_obj)

        db_session.commit()

        # pass db_session explicitly so view_item uses the same session
        result = view_item(
            menu_id,
            current_user=current_user,
            lang=lang,
            message='record_saved',
            db_session=db_session
        )
        return result

    except ValueError as e:
        if db_session:
            db_session.rollback()

        logger.error(f"ValueError in save_menu_setup: {str(e)}")

        error_dict = {}
        error_msg = str(e)
        pattern = r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}'
        matches = re.findall(pattern, error_msg)

        if matches:
            try:
                error_dict = ast.literal_eval(matches[0])
            except (ValueError, SyntaxError):
                error_dict = {'validation_error': error_msg}
        else:
            error_dict = {'validation_error': error_msg}

        return {
            'ok': False,
            'status': 400,
            'title': ___('notice', {}, lang),
            'message': ___('validation_failed', {}, lang),
            'error': error_dict,
            'data': {}
        }

    except Exception as e:
        if db_session:
            db_session.rollback()
        logger.error(f"Exception in save_menu_setup: {str(e)}", exc_info=True)
        raise e

    finally:
        if db_session:
            db_session.close()


def get_header():
    return [
        {"field": "id", "text": "ID"},
        {"field": "description", "text": "Description"},
        {"field": "ordering", "text": "Ordering"},
    ]


def get_header_sub():
    return {
        'sub_menu': [
            {"field": "id", "text": "ID"},
            {"field": "main_id", "text": "Main ID"},
            {"field": "label", "text": "Label"},
            {"field": "type", "text": "Type"},
            {"field": "url", "text": "URL"},
            {"field": "icon", "text": "Icon"},
            {"field": "module_id", "text": "Module ID"},
            {"field": "name", "model": TBL_MODULE, "label": "module_name"},
        ]
    }


# single canonical view_item that always receives db_session explicitly
def view_item(id, current_user=None, lang: str = 'en', message='', db_session: Session = None):
    """
    View menu item details. Callers must pass db_session explicitly.
    """
    own_session = False
    try:
        if not db_session:
            db_session = next(get_db())
            own_session = True

        header = get_header()
        model = TBL_MENU
        module = 'Menu'
        sub_models = {'sub_menu': TBL_SUB_MENU}

        query = db_session.query(model).filter(model.id == id)

        fields = []
        header_extended = list(header)
        header_extended.extend([
            {'field': 'company_id'},
            {'field': 're_created_by'},
            {'field': 're_updated_by'},
            {'field': 're_created_at'},
            {'field': 're_updated_at'},
            {'field': 're_status'},
            {'field': 're_version'},
            {'field': 'branch_id'},
            {'field': 'authorization'},
            {'field': 'flow_status', 'text': 'Flow Status'}
        ])

        for f in header_extended:
            try:
                if f.get('model') or f.get('label'):
                    fields.append(
                        getattr(f.get('model', model), f.get('field')).label(f.get('label', f.get('field')))
                    )
                else:
                    fields.append(eval(f'model.{f.get("field")}'))
            except (AttributeError, NameError):
                continue

        obj = query.with_entities(*fields).first()

        if not obj:
            return {
                'ok': False,
                'status': 404,
                'title': 'View Records',
                'message': 'record not found',
                'error': {},
                'data': {}
            }

        if hasattr(obj, '_mapping'):
            obj_dict = dict(obj._mapping)
        else:
            obj_dict = jsonable_encoder(obj)

        # pass db_session into get_authorization
        item = {'item': get_authorization(obj_dict, db_session)}

        sub_item = {}
        for sub_key, sub_model in sub_models.items():
            sub_fields = get_header_sub().get(sub_key, [])
            query_fields = []

            for f in sub_fields:
                try:
                    if f.get('model') or f.get('label'):
                        query_fields.append(
                            getattr(f.get('model', sub_model), f.get('field')).label(f.get('label', f.get('field')))
                        )
                    else:
                        query_fields.append(eval(f'sub_model.{f.get("field")}'))
                except (AttributeError, NameError):
                    continue

            if query_fields:
                sub_obj_query = (
                    db_session.query(sub_model)
                    .outerjoin(TBL_MODULE, TBL_MODULE.id == sub_model.module_id)
                    .filter(sub_model.parent_id == id)
                )
                sub_objects = sub_obj_query.with_entities(*query_fields).all()
            else:
                sub_objects = []

            sub_item[sub_key] = [
                dict(o._mapping) if hasattr(o, '_mapping') else jsonable_encoder(o)
                for o in sub_objects
            ]

        if sub_item:
            item['sub_items'] = sub_item

        data = jsonable_encoder(item)

        return {
            'ok': True,
            'status': 200,
            'title': module,
            'message': message or core_lib.get_lang('data_retrieved_successful', lang=lang),
            'error': {},
            'data': data,
            'request_id': getattr(app.state, 'request_id', '')
        }

    except Exception as e:
        logger.error(f"Exception in view_item: {str(e)}", exc_info=True)
        if db_session:
            try:
                db_session.rollback()
            except Exception as rollback_error:
                logger.error(f"Error during rollback: {str(rollback_error)}")
        raise e

    finally:
        if own_session and db_session:
            try:
                db_session.close()
            except Exception as close_error:
                logger.error(f"Error closing session: {str(close_error)}")


# get_authorization now receives db explicitly — no more bare global `db`
def get_authorization(item, db: Session):
    if item:
        auth = item.get('authorization', [])
        if auth:
            auth_data = []
            for a in auth:
                if a.get('id') != 'SYSTEM':
                    user_obj = db.query(TBL_USER).filter(TBL_USER.id == a.get('id')).first()
                    a.update({'name': f'{user_obj.first_name} {user_obj.last_name}' if user_obj else ''})
                else:
                    a.update({'name': 'SYSTEM'})
                auth_data.append(a)
            item.update({'authorization': auth_data})

        if item.get('re_created_by') == 'SYSTEM':
            item.update({'re_created_by_name': 'SYSTEM'})
        else:
            uc_obj = db.query(TBL_USER).filter(TBL_USER.id == item.get('re_created_by')).first()
            item.update({'re_created_by_name': f'{uc_obj.first_name} {uc_obj.last_name}' if uc_obj else ''})

        uu_obj = db.query(TBL_USER).filter(TBL_USER.id == item.get('re_updated_by')).first()
        item.update({'re_updated_by_name': f'{uu_obj.first_name} {uu_obj.last_name}' if uu_obj else ''})

        branch_obj = db.query(TBL_BRANCH).filter(TBL_BRANCH.id == item.get('branch_id')).first()
        item.update({'branch_name': branch_obj.name if branch_obj else ''})

    return item


@app.put("/api/v1/wb/update-menu-setup", tags=['Menu'])
async def update_menu_setup(
    id          : str,
    item        : Annotated[MenuSchema, Body(embed=True)],
    sub_item    : SubMenuListSchema,
    current_user: Annotated[User, Depends(get_current_active_user)],
    lang        : str = "kh",
    # accept db from Depends so all queries use the same managed session
    db          : Session = Depends(get_db)
):
    try:
        item         = item.dict()
        sub_item     = sub_item.dict() if sub_item else None
        model        = TBL_MENU
        sub_models   = {'sub_menu': TBL_SUB_MENU}
        schema       = MenuSchema
        moduleList   = __import__("main")
        item.update({'id': id})
        item.pop('re_version', None)
        item.pop('system_date', None)
        item.pop('re_created_by', None)
        item.pop('re_created_at', None)
        item.pop('re_updated_by', None)
        item.pop('re_updated_at', None)
        auth_data = []

        data = dict(item)
        data.update(dict(is_manual_validation=True, id=id, lang=lang, current_user=jsonable_encoder(current_user)))
        schema(**data)

        system_date_obj = db.query(TBL_SYSTEM_DATE).first()
        Dict = {
            're_updated_by': current_user.id,
            're_updated_at': core_lib.get_str_datetime_now(),
            'system_date'  : system_date_obj.current_system_date,
            'branch_id'    : current_user.token_working_branch_id,
            'company_id'   : current_user.token_working_company_id,
            'authorization': auth_data
        }
        message = 'record_updated'
        obj = db.query(model).filter(model.id == id)

        if obj.first():
            hm = getattr(moduleList, str(model.__name__) + '_HISTORY')
            # pass db to copy_data_from
            copy_data_from(moduleList, model, sub_models, '', '_HISTORY', id, data=Dict, db=db)
            h_obj = db.query(hm.re_version).filter(hm.id == id).order_by(hm.re_version.desc()).first()
            r_v = int(h_obj.re_version if h_obj else obj.first().re_version) + 1
            Dict.update({'re_version': r_v})

            auth_data.append({
                'id': current_user.id,
                'status': 'APPROVED',
                'datetime': core_lib.get_str_datetime_now()
            })
            Dict.update({'authorization': auth_data})
            item.update(Dict)
            obj.update(item)

            if sub_item:
                for sub_item_key, list_sub_item in sub_item.items():
                    sub_model = sub_models[sub_item_key]
                    db.query(sub_model).filter(sub_model.parent_id == id).delete()

                    if list_sub_item:
                        for st in list_sub_item:
                            sub_id = st.get('id', '')
                            st.update(Dict)
                            st.update({'parent_id': id, 'id': sub_id})
                            s_obj = sub_model(**st)
                            db.add(s_obj)

            db.commit()
            # pass db_session so view_item uses the same session
            result = view_item(id, current_user=current_user, lang=lang, message=message, db_session=db)
            return result

        else:
            raise HTTPException(status_code=404, detail=core_lib.get_lang("record_not_found", lang=current_user.language))

    except ValueError as e:
        print('ValueError', str(e))
        pattern = r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}'
        matches = re.findall(pattern, str(e))
        return {
            'ok': False,
            'status': 400,
            'title': ___('notice', {}, lang),
            'message': ___('try_again_in_title', {}, lang),
            'error': ast.literal_eval(matches[0]) if matches else {},
            'data': {}
        }

    except Exception as e:
        db.rollback()
        logger.error(f"[CRUDPUT] Error in put operation: {str(e)}")
        raise e

    finally:
        db.close()

# copy_data_from now receives db explicitly
def copy_data_from(moduleList, model, sub_models, source_type, destination_type, id, data={}, filters={}, db: Session = None):
    modelDel = getattr(moduleList, str(model.__name__) + source_type)
    f_arr = [modelDel.id == id]

    if filters:
        for f, v in filters:
            f_arr.append(getattr(modelDel, f) == v)

    obj = db.query(modelDel).filter(*f_arr)

    if obj.first():
        ObjList = []
        DataDict = {}

        for column in model.__table__.columns:
            DataDict.update({column.name: getattr(obj.first(), str(column.name))})

        DataDict.update(data)

        # get the max re_version from history and increment to avoid duplicate key
        ModelObj = getattr(moduleList, str(model.__name__) + destination_type)
        existing_max = db.query(func.max(ModelObj.re_version))\
            .filter(ModelObj.id == id)\
            .filter(ModelObj.company_id == DataDict.get('company_id'))\
            .scalar()
        DataDict['re_version'] = (existing_max or 0) + 1

        DataEntry = ModelObj(**DataDict)
        ObjList.append(DataEntry)

        for sm in sub_models.values():
            modelObj = getattr(moduleList, str(sm.__name__) + destination_type)
            if source_type:
                sm = getattr(moduleList, str(sm.__name__) + source_type)

            s_objs = db.query(sm).filter(sm.parent_id == id).all()

            for s_obj in s_objs:
                DataDict = {}
                for column in sm.__table__.columns:
                    DataDict.update({column.name: getattr(s_obj, str(column.name))})

                # fill null required fields
                if not DataDict.get('company_id'):
                    DataDict['company_id'] = data.get('company_id', '')
                if not DataDict.get('branch_id'):
                    DataDict['branch_id'] = data.get('branch_id', '')
                if not DataDict.get('re_created_by'):
                    DataDict['re_created_by'] = data.get('re_updated_by', '')
                if not DataDict.get('re_updated_by'):
                    DataDict['re_updated_by'] = data.get('re_updated_by', '')

                # get max re_version for each sub record too
                existing_sub_max = db.query(func.max(modelObj.re_version))\
                    .filter(modelObj.id == s_obj.id)\
                    .scalar()
                DataDict['re_version'] = (existing_sub_max or 0) + 1

                DataEntry = modelObj(**DataDict)
                ObjList.append(DataEntry)

        db.add_all(ObjList)

        return True, 'Record was copied successfully'

    return False, 'Record not found'