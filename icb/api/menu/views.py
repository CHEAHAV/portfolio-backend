import time, uuid, os, ast, re
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
from icb.api.user.models import TBL_USER, TBL_USER_LOCATION_ASSIGNMENT
from icb.api.role.models import TBL_ROLE, TBL_ROLE_MODULE
from icb.core.role_delegation import get_active_delegated_module_ids, get_effective_role_ids
from .models import *
from .schemas import *
from main import app
import icb.core.lib as core_lib
___ = core_lib.get_lang

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
        
    def get_vsi_query(self, record_type=''):
        model = getattr(self.moduleList, str(self.sub_models.get('sub_menu').__name__) + record_type)
        query = db.query(model).outerjoin(TBL_MODULE, TBL_MODULE.id == model.module_id)
        return { 'sub_menu': query }
        
crud = MENU_CRUD_API('Menu', 'menus', TBL_MENU, 
    { 'sub_menu': TBL_SUB_MENU }, 
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
        return db.query(model).outerjoin(TBL_MODULE, TBL_MODULE.id == model.module_id)
        
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
    # Fetch main menus
    menus = db.query(TBL_SUB_MENU).\
    filter(TBL_SUB_MENU.parent_id == menu_id).\
    filter(or_(TBL_SUB_MENU.main_id.is_(None),TBL_SUB_MENU.main_id=='')).\
    order_by(TBL_SUB_MENU.ordering).all()

    # Helper function to fetch sub menus
    def fetch_sub_menus(parent_id,menu_id):
        return db.query(
                TBL_SUB_MENU.id,
                TBL_MENU_ITEM.label,
                TBL_MENU_ITEM.icon,
                TBL_MENU_ITEM.type,
                TBL_MENU_ITEM.module_id,
                TBL_MENU_ITEM.url,
            ).\
            outerjoin(TBL_MENU_ITEM,TBL_MENU_ITEM.id==TBL_SUB_MENU.id).\
            filter(TBL_SUB_MENU.main_id == str(parent_id)).\
            filter(TBL_SUB_MENU.parent_id == str(menu_id)).\
            order_by(TBL_SUB_MENU.ordering).all()

    def get_list_sub_menu(parent_id, menu_id, role_modules=[],user_role=None, list_permission_type=False):
        menu_list = []
        sub_menus = fetch_sub_menus(parent_id,menu_id)
        if sub_menus:
            for sub_menu in sub_menus:
                if not list_permission_type and str(sub_menu.type).lower() == 'permission':
                    continue

                menus    = fetch_sub_menus(sub_menu.id,menu_id)
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
    
    # Build menu structure
    menu_list = []
    user_role = get_current_role(current_user, db)
    role_modules = get_role_modules(current_user, db)
    menu_types = ['standard','permission'] if list_permission_type else ['standard']
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
    # Get menu id

    menu_id = "1"
    return get_menu_for_render(menu_id, current_user, db, lang)
    
    


@app.post("/api/v1/wb/save-menu-setup", tags=['Menu'])
async def save_menu_setup(
    item        : Annotated[MenuSchema, Body(embed=True)],
    sub_item    : SubMenuListSchema,
    current_user: Annotated[User, Depends(get_current_active_user)],
    lang        : str = "kh",
):
    try:
        moduleList = __import__("main")
        model = TBL_MENU
        sub_models = { 'sub_menu': TBL_SUB_MENU }
        item = item.dict()
        schema = MenuSchema
        sub_item = sub_item.dict() if sub_item else None
        id = ''
        if 'id' in item and item['id']:
            id = item['id']
        else:
            id = core_lib.get_module_id('Menu')
        
        v_obj = db.query(model).filter(model.id == id).first()
        if v_obj:
            return render_detail(status=False, title=___('notice', {}, lang), module='data', 
                                message=___('record_id_already_exist', {}, lang), 
                                error={'id':___('record_id_already_exist', {}, lang)}
                                )
        
        else:
            modelDel = getattr(moduleList, str(model.__name__) + "_DELETED")
            v_obj = db.query(modelDel).filter(modelDel.id == id).first()
            if v_obj:
                return render_detail(status=False, title=___('notice', {}, lang), module='data', 
                                message=___('record_id_already_exist', {}, lang), 
                                error={'id':___('record_id_already_exist', {}, lang)}
                                )
        
        # Get form data
        data = dict(item)
        data.update(dict(is_manual_validation=True, id=id, lang=lang, current_user=jsonable_encoder(current_user)))
        # Re-validation with language
        schema(**data)

        re_status    = 'AUTH'
        re_type      = ''
        ntf_msg      = ''
        message      = 'record_saved'
        main_model   = model
        auth_data    = []
        datetime_now = str(core_lib.get_datetime_now())
        
        auth_data.append({
            'id'      : current_user.id,
            'status'  : 'APPROVED',
            'datetime': datetime_now
        })
            
        system_date_obj = db.query(TBL_SYSTEM_DATE).first()
        Dict = {
            'id'           : id,
            're_version'   : 0,
            'authorization': auth_data,
            're_status'    : re_status,
            're_created_by': current_user.id,
            're_created_at': datetime_now,
            're_updated_by': current_user.id,
            're_updated_at': datetime_now,
            'system_date'   : system_date_obj.current_system_date,
            'branch_id'    : current_user.token_working_branch_id,
            'company_id'   : current_user.token_working_company_id
        }
        
        item.update(Dict)
        obj = main_model(**item)
        db.add(obj)
    
        if sub_item:
            for sub_item_key, list_sub_item in sub_item.items():
                sub_model = sub_models[sub_item_key]
                if list_sub_item:
                    for st in list_sub_item:
                        sub_id = st.get('id','')
                        st.update(Dict)
                        st.update({'parent_id': id, 'id': sub_id})
                        s_obj = sub_model(**st)
                        db.add(s_obj)
        
        db.commit()
        obj = view_item(id, current_user=current_user, lang=lang, message=message)
        return obj
        
    except ValueError as e:
        print(str(e))
        # Regex pattern to match dictionaries including nested ones
        pattern = r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}'
        # Find all matches in the string
        matches = re.findall(pattern, str(e))
        return_data = dict(
            status  = False,
            title   = ___('notice', {}, lang),
            module  = 'data',
            message = ___('try_again_in_title', {}, lang),
            error   = ast.literal_eval(matches[0])
        )
        return render_detail(**return_data)

    except Exception as e:
        logger.error(e)
        db.rollback()
        raise e

    finally:
        db.close()

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

def view_item(id, current_user=None, lang: str = 'en', message=''):
    try:
        header      = get_header()
        model       = TBL_MENU
        module      = 'Menu'
        sub_models  = { 'sub_menu': TBL_SUB_MENU }
        obj = db.query(model).filter(model.id == id)
        
        fields = []
        header.append({'field': 'company_id'})
        header.append({'field': 're_created_by'})
        header.append({'field': 're_updated_by'})
        header.append({'field': 're_created_at'})
        header.append({'field': 're_updated_at'})
        header.append({'field': 're_status'})
        header.append({'field': 're_version'})
        header.append({'field': 'branch_id'})
        header.append({'field': 'authorization'})
        header.append({'field': 'flow_status', 'text': 'Flow Status'})
        
        for f in header:
            if f.get('model') or f.get('label'):
                if f.get('concat'):
                    concat = []
                    for c in f.get('concat'):
                        if len(concat) > 0:
                            concat.append(c.get('separator', ' '))
                        else:
                            concat.append(c.get('separator', ''))
                            
                        concat.append(getattr(c.get('model', model), c.get('field')))
                    fields.append(func.concat(*concat).label(f.get('label')))
                
                elif f.get('func.json_agg'):
                    aggregate = []
                    f1 = f.get('func.json_agg')[0]
                    for c in f.get('func.json_agg', []):
                        aggregate.extend([c.get('field',''),getattr(c.get('model'), c.get('field'))])
                    
                    fields.append(func.coalesce(func.json_agg(
                        func.json_build_object(*aggregate)
                    ).filter(getattr(f1.get('model'), f1.get('field')).isnot(None)),
                    func.cast([], JSON)).label(f.get('label')))
                elif f.get('case'):
                    case_expr = get_case_expr(f, model)
                    fields.append(case_expr)          
                else:
                    fields.append(getattr(f.get('model', model), f.get('field')).label(f.get('label')))
            
            else:
                fields.append(eval(f'model.{f.get("field")}'))
        
        obj = obj.with_entities(*fields).first()
        
        if not obj:
            return response_msg('View records', 'record not found', 404, False, error={}, data={})
            
        item = {'item': get_authorization(jsonable_encoder(obj))}
        sub_item = {}

        sub_obj  = {
            'sub_menu'  :   db.query(sub_models.get('sub_menu'))\
                            .outerjoin(TBL_MODULE, TBL_MODULE.id == sub_models.get('sub_menu').module_id)
        }
        for k, sm in sub_models.items(): 
            sub_model = sm
            s_obj = sub_obj.get(k)
            s_fields = get_header_sub().get(k, [])
            fields = []
            for f in s_fields:
                if f.get('model') or f.get('label'):
                    if f.get('concat'):
                        concat = []
                        for c in f.get('concat'):
                            if len(concat) > 0:
                                concat.append(c.get('separator', ' '))
                            else:
                                concat.append(c.get('separator', ''))
                            
                            concat.append(getattr(c.get('model', sub_model), c.get('field')))
                        fields.append(func.concat(*concat).label(f.get('label')))
                        
                    elif f.get('func.json_agg'):
                        aggregate = []
                        f1 = f.get('func.json_agg')[0]
                        for c in f.get('func.json_agg', []):
                            aggregate.extend([c.get('field',''),getattr(c.get('model'), c.get('field'))])
                            
                        fields.append(func.coalesce(func.json_agg(
                            func.json_build_object(*aggregate)
                        ).filter(getattr(f1.get('model'), f1.get('field')).isnot(None)),
                        func.cast([], JSON)).label(f.get('label')))
                    
                    elif f.get('case'):
                        case_expr = get_case_expr(f, model)
                        fields.append(case_expr)    
                            
                    else:
                        fields.append(getattr(f.get('model', sub_model), f.get('field')).label(f.get('label')))
                    
                else:
                    fields.append(eval(f'sub_model.{f.get("field")}'))
            
            s_obj = s_obj.with_entities(*fields).filter(sub_model.parent_id == id)
            s_obj = s_obj.all()
            sub_item.update({k: jsonable_encoder(s_obj)})

        if sub_item:
            item.update({'sub_items': sub_item})

        data = jsonable_encoder(item)
      
        return {
            'ok'        : True,
            'status'    : 200,
            'title'     : module,
            "message"   : message if message else core_lib.get_lang('data_retrieved_successful', lang=lang),
            "error"     : {},
            'data'      : data,
            "request_id": app.state.request_id
        }

    except Exception as e:
        db.rollback()
        logger.error(e)
        raise e
    finally:
        db.close()

def get_authorization(item):
    if item:
      auth = item.get('authorization',[])
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
):
    try:
        item         = item.dict()
        sub_item     = sub_item.dict() if sub_item else None
        model        = TBL_MENU
        sub_models   = { 'sub_menu': TBL_SUB_MENU }
        schema       = MenuSchema
        moduleList   = __import__("main")
        current_user = current_user
        item.update({'id': id})
        item.pop('re_version', None)
        item.pop('system_date', None)
        item.pop('re_created_by', None)
        item.pop('re_created_at', None)
        item.pop('re_updated_by', None)
        item.pop('re_updated_at', None)
        auth_data = []
      
        # Get form data
        data = dict(item)
        data.update(dict(is_manual_validation=True, id=id, lang=lang, current_user=jsonable_encoder(current_user)))
        # Re-validation with language
        schema(**data)
        system_date_obj = db.query(TBL_SYSTEM_DATE).first()
        Dict = {
            're_updated_by': current_user.id,
            're_updated_at': core_lib.get_str_datetime_now(),
            'system_date'   : system_date_obj.current_system_date,
            'branch_id'    : current_user.token_working_branch_id,
            'company_id'   : current_user.token_working_company_id,
            'authorization': auth_data
        }
        message = 'record_updated'
        obj = db.query(model).filter(model.id == id)      

        if obj.first():
            ntf_msg = ''
            hm = getattr(moduleList, str(model.__name__) + '_HISTORY')

            copy_data_from(moduleList,model,sub_models,'', '_HISTORY', id)
            h_obj = db.query(hm.re_version).filter(hm.id == id).order_by(hm.re_version.desc()).first()
            r_v = int(h_obj.re_version if h_obj else obj.first().re_version) + 1
            Dict.update({'re_version': r_v})
            
            auth_data.append({
                'id': current_user.id,
                'status': 'APPROVED',
                'datetime': core_lib.get_str_datetime_now()
            })
            Dict.update({'authorization': auth_data})
            # Dict.update({'re_version': int(obj.first().re_version) + 1})
            item.update(Dict)
            obj.update(item)

            if sub_item:
                for sub_item_key, list_sub_item in sub_item.items():
                    sub_model = sub_models[sub_item_key]
                    db.query(sub_model).filter(sub_model.parent_id == id).delete()

                    if list_sub_item:
                        for st in list_sub_item:
                            sub_id = st.get('id','')
                            st.update(Dict)
                            st.update({'parent_id': id, 'id': sub_id})

                            s_obj = sub_model(**st)
                            db.add(s_obj)
            
            db.commit()
            obj = view_item(id, current_user=current_user, message=message)
        
            return obj

        else:
            raise HTTPException(status_code=404, detail=core_lib.get_lang("record_not_found", lang=current_user.language))

    except ValueError as e:
        print('ValueError', str(e))
        # Regex pattern to match dictionaries including nested ones
        pattern = r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}'
        # Find all matches in the string
        matches = re.findall(pattern, str(e))
        return_data = dict(
            status=False,
            title=___('notice', {}, lang),
            module='data',
            message=___('try_again_in_title', {}, lang),
            error=ast.literal_eval(matches[0])
        )
        return render_detail(**return_data)
        
    except Exception as e:
        db.rollback()
        logger.error(f"[CRUDPUT] Error in put operation: {str(e)}")
        raise e
        
    finally:
        db.close()

def copy_data_from(moduleList,model,sub_models,source_type, destination_type, id, data={}, filters={}):
    modelDel = getattr(moduleList, str(model.__name__) + source_type)
    f_arr = [modelDel.id == id]
    
    if filters:
      for f,v in filters:
        f_arr.append(getattr(modelDel,f)==v)
        
    obj = db.query(modelDel).filter(*f_arr)
    
    if (obj.first()):
      ObjList = []
      DataDict = {}

      for column in model.__table__.columns:
        DataDict.update({column.name: getattr(obj.first(), str(column.name))})
      
      DataDict.update(data)
      ModelObj = getattr(moduleList, str(model.__name__) + destination_type)
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

          DataEntry = modelObj(**DataDict)
          ObjList.append(DataEntry)

      db.add_all(ObjList)

      return True, 'Record was copied successfully'

    return False, 'Record not found'
