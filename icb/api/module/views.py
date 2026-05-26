from main import app
from icb.core.crud_api import *
from icb.core.lib import get_module_id, get_lang as __
from .models import *
from .schemas import *
import icb.core.lib as core_lib
from icb.api.user.models import TBL_USER, TBL_USER_LOCATION_ASSIGNMENT
from icb.api.role.models import TBL_ROLE, TBL_ROLE_MODULE
from icb.lib.render_api import ResponseModel
from icb.core.lib import check_is_superuser

class MODULE_CRUD_API(CRUDAPI):
    query_fields = ['name']
    def get_header(self):
        return [
            {"field": "id", "text": "ID"},
            {"field": "name", "text": "Name"},
            {"field": "num_of_auth", "text": "num_of_auth"},
            {"field": "url", "text": "URL"},
            {"field": "model", "text": "Table"},
            {"field": "mask_field", "text": "Mask Field"},
            {"field": "list_view", "text": "List View"},
            {"field": "query_list", "text": "Query List"},
            {"field": "enable_log", "text": "Enable Log"},
            {"field": "log_action", "text": "Log Action"},
        ]
    
    def before_save(self):
        module_name = self.item['name']
        obj = self.db.query(TBL_MODULE.id).filter(
            TBL_MODULE.name==module_name
        ).first()
        if obj:
            return False, {'name':'Module name is already exist.'}
        return True, ''
        
    def before_update(self):
        module_name = self.item['name']
        obj = self.db.query(TBL_MODULE.id).filter(
            TBL_MODULE.name==module_name,
            TBL_MODULE.id!=self.id,
        ).first()
        if obj:
            return False, {'name':'Module name is already exist.'}
        return True, ''

crud = MODULE_CRUD_API('Module','modules', TBL_MODULE,{},schema=ModuleSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Module'])


class FORM_MODULE_CRUD_API(CRUDAPI):
    query_fields = ['id']
    def get_header(self):
        return [
            {"field": "id", "text": "ID"},
            {"field": "module_id", "text": "Module ID"},
            {"field": "name", "text": "Module Name", "model": TBL_MODULE, "label": "module_name"},
            {"field": "num_of_auth", "text": "Number of Authorize"},
            {"field": "list_view", "text": "List View"},
            {"field": "query_list", "text": "Query List"},
        ]
    
    def get_list_query(self, model):
        return db.query(model).outerjoin(TBL_MODULE, TBL_MODULE.id==model.module_id)
    
    def before_save(self):
        module_id = self.item['module_id']
        obj = self.db.query(TBL_FORM_MODULE.id).filter(
            TBL_FORM_MODULE.module_id==module_id,
            TBL_FORM_MODULE.company_id==self.current_user.token_working_company_id,
        ).first()
        if obj:
            return False, {'module_id':'Module name is already exist.'}
        
        return True, ''
        
    def before_update(self):
        module_id = self.item['module_id']
        obj = self.db.query(TBL_FORM_MODULE.id).filter(
            TBL_FORM_MODULE.id!=self.id,
            TBL_FORM_MODULE.module_id==module_id,
            TBL_FORM_MODULE.company_id==self.current_user.token_working_company_id,
        ).first()
        if obj:
            return False, {'module_id':'Module name is already exist.'}
        
        return True, ''
        
crud = FORM_MODULE_CRUD_API('FormModule','form-modules', TBL_FORM_MODULE,{},schema=FormModuleSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Module'])


class AUTO_ID_CRUD_API(CRUDAPI):
    query_fields = ['id']
    def get_header(self):
        return [
            {"field": "id", "text": "ID"},
            {"field": "module_id", "text": "Module ID"},
            {"field": "name", "text": "Module Name", "model": TBL_MODULE, "label": "module_name"},
            {"field": "id_type", "text": "ID Type"},
            {"field": "id_prefix", "text": "ID Prefix"},
            {"field": "id_index", "text": "ID Index"},
            {"field": "id_date_format", "text": "ID Date Format"},
            {"field": "id_serial_length", "text": "ID Serial Length"},
            {"field": "id_prev_date", "text": "ID Previous Date"}
        ]
    
    def get_list_query(self, model):
        return db.query(model).outerjoin(TBL_MODULE, TBL_MODULE.id==model.module_id)
    
    def before_save(self):
        module_id = self.item['module_id']
        obj = self.db.query(TBL_AUTO_ID.id).filter(
            TBL_AUTO_ID.module_id==module_id,
            TBL_AUTO_ID.branch_id==self.current_user.token_working_branch_id,
            TBL_AUTO_ID.company_id==self.current_user.token_working_company_id,
        ).first()
        if obj:
            return False, {'module_id':'Module name is already exist for current branch.'}
        
        return True, ''
        
    def before_update(self):
        module_id = self.item['module_id']
        obj = self.db.query(TBL_AUTO_ID.id).filter(
            TBL_AUTO_ID.id!=self.id,
            TBL_AUTO_ID.module_id==module_id,
            TBL_AUTO_ID.branch_id==self.current_user.token_working_branch_id,
            TBL_AUTO_ID.company_id==self.current_user.token_working_company_id,
        ).first()
        if obj:
            return False, {'module_id':'Module name is already exist for current branch.'}
        
        return True, ''
        
crud = AUTO_ID_CRUD_API('AutoID','auto-ids', TBL_AUTO_ID,{},schema=AutoIDSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Auto ID'])


# def form_data(lang):
#     id = get_module_id("Module")
#     return {
#             "ok": True,
#             "status": 200,
#             "title": __("module", {}, lang),
#             "message": "",
#             "error": {},
#             "data": {
#                 "form": {
#                     "tab": [
#                         {
#                             "field": [
#                                 {
#                                     "choices": [],
#                                     "default": get_module_id("Module"),
#                                     "disabled": True,
#                                     "file": {},
#                                     "hot_field": [],
#                                     "hot_select_field": [],
#                                     "label": __("id", {}, lang),
#                                     "description": "",
#                                     "money_field": {},
#                                     "name": "ID",
#                                     "remote_url_for": "",
#                                     "required": "*",
#                                     "set_visible": False,
#                                     "set_width": 4,
#                                     "type": "TextField"
#                                 },
#                                 {
#                                     "choices": [],
#                                     "default": "",
#                                     "disabled": False,
#                                     "file": {},
#                                     "hot_field": [],
#                                     "hot_select_field": [],
#                                     "label": __("name", {}, lang),
#                                     "description": "",
#                                     "money_field": {},
#                                     "name": "Name",
#                                     "remote_url_for": "",
#                                     "required": "*",
#                                     "set_visible": False,
#                                     "set_width": 4,
#                                     "type": "TextField"
#                                 },
#                                 {
#                                     "choices": [],
#                                     "default": "",
#                                     "disabled": False,
#                                     "file": {},
#                                     "hot_field": [],
#                                     "hot_select_field": [],
#                                     "label": __("name_lc", {}, lang),
#                                     "description": "",
#                                     "money_field": {},
#                                     "name": "Name LC",
#                                     "remote_url_for": "",
#                                     "required": "*",
#                                     "set_visible": False,
#                                     "set_width": 4,
#                                     "type": "TextField"
#                                 },
#                                 {
#                                     "choices": [],
#                                     "default": 0,
#                                     "disabled": False,
#                                     "file": {},
#                                     "hot_field": [],
#                                     "hot_select_field": [],
#                                     "index": 1,
#                                     "label": __("number_of_authorization", {}, lang),
#                                     "description": "",
#                                     "money_field": {},
#                                     "name": "Number of Authorization",
#                                     "remote_url_for": "",
#                                     "required": "",
#                                     "set_visible": False,
#                                     "set_width": 4,
#                                     "type": "IntegerField"
#                                 },
#                                 {
#                                     "choices": [
#                                         {
#                                             "label": __("uuid", {}, lang),
#                                             "value": "UUID"
#                                         },
#                                         {
#                                             "label": __("sequencial", {}, lang),
#                                             "value": "Sequencial"
#                                         },
#                                         {
#                                             "label": __("sequencial_by_day", {}, lang),
#                                             "value": "SequencialByDay"
#                                         },
#                                         {
#                                             "label": __("sequencial_by_month", {}, lang),
#                                             "value": "SequencialByMonth"
#                                         },
#                                         {
#                                             "label": __("sequencial_by_year", {}, lang),
#                                             "value": "SequencialByYear"
#                                         }
#                                     ],
#                                     "default": "UUID",
#                                     "disabled": False,
#                                     "file": {},
#                                     "hot_field": [],
#                                     "hot_select_field": [],
#                                     "label": __("id_type", {}, lang),
#                                     "description": "",
#                                     "money_field": {},
#                                     "name": "ID type",
#                                     "remote_url_for": "",
#                                     "required": "*",
#                                     "set_visible": False,
#                                     "set_width": 4,
#                                     "type": "QuerySelectField"
#                                 },
#                                 {
#                                     "choices": [],
#                                     "default": "",
#                                     "disabled": False,
#                                     "file": {},
#                                     "hot_field": [],
#                                     "hot_select_field": [],
#                                     "label": __("url", {}, lang),
#                                     "description": "",
#                                     "money_field": {},
#                                     "name": "URL",
#                                     "remote_url_for": "",
#                                     "required": "*",
#                                     "set_visible": False,
#                                     "set_width": 4,
#                                     "type": "TextField"
#                                 },
#                                 {
#                                     "choices": [],
#                                     "default": "",
#                                     "disabled": False,
#                                     "file": {},
#                                     "hot_field": [],
#                                     "hot_select_field": [],
#                                     "label": __("id_prefix", {}, lang),
#                                     "description": "",
#                                     "money_field": {},
#                                     "name": "ID Prefix",
#                                     "remote_url_for": "",
#                                     "required": "",
#                                     "set_visible": False,
#                                     "set_width": 4,
#                                     "type": "TextField"
#                                 },
#                                 {
#                                     "choices": [],
#                                     "default": 1,
#                                     "disabled": False,
#                                     "file": {},
#                                     "hot_field": [],
#                                     "hot_select_field": [],
#                                     "index": 1,
#                                     "label": __("id_index", {}, lang),
#                                     "description": "",
#                                     "money_field": {},
#                                     "name": "ID Index",
#                                     "remote_url_for": "",
#                                     "required": "",
#                                     "set_visible": False,
#                                     "set_width": 4,
#                                     "type": "IntegerField"
#                                 },
#                                 {
#                                     "choices": [],
#                                     "default": "Ymd",
#                                     "disabled": False,
#                                     "file": {},
#                                     "hot_field": [],
#                                     "hot_select_field": [],
#                                     "index": 1,
#                                     "label": __("id_date_format", {}, lang),
#                                     "description": "",
#                                     "money_field": {},
#                                     "name": "ID Date Format",
#                                     "remote_url_for": "",
#                                     "required": "",
#                                     "set_visible": False,
#                                     "set_width": 4,
#                                     "type": "TextField"
#                                 },
#                                 {
#                                     "choices": [],
#                                     "default": 1,
#                                     "disabled": False,
#                                     "file": {},
#                                     "hot_field": [],
#                                     "hot_select_field": [],
#                                     "index": 1,
#                                     "label": __("id_serial_length", {}, lang),
#                                     "description": "",
#                                     "money_field": {},
#                                     "name": "ID Serial Length",
#                                     "remote_url_for": "",
#                                     "required": "",
#                                     "set_visible": False,
#                                     "set_width": 4,
#                                     "type": "IntegerField"
#                                 },
#                                 {
#                                     "choices": [
#                                         {
#                                             "label": __("standard", {}, lang),
#                                             "value": "Standard"
#                                         },
#                                         {
#                                             "label": __("custom", {}, lang),
#                                             "value": "Custom"
#                                         },
#                                         {
#                                             "label": __("label", {}, lang),
#                                             "value": "Label"
#                                         }
#                                     ],
#                                     "default": "Standard",
#                                     "disabled": False,
#                                     "file": {},
#                                     "hot_field": [],
#                                     "hot_select_field": [],
#                                     "label": __("type", {}, lang),
#                                     "description": "",
#                                     "money_field": {},
#                                     "name": "Type",
#                                     "remote_url_for": "",
#                                     "required": "*",
#                                     "set_visible": False,
#                                     "set_width": 4,
#                                     "type": "QuerySelectField"
#                                 },
#                             ],
#                             "index": "0",
#                             "multi_value": False,
#                             "title": "General"
#                         }
#                     ]
#                 },
#                 "meta_data": {
#                     "record_id": id,
#                     "action": [
#                         {
#                             "color": "#FFFFFF",
#                             "icon": "",
#                             "text": __("save_record", {}, lang),
#                             "method": "post",
#                             "url": "/v1/wb/modules"
#                         },
#                         {
#                             "color": "#FF0000",
#                             "icon": "",
#                             "text": __("edit", {}, lang),
#                             "method": "get",
#                             "url": "/v1/wb/modules/live/" + id
#                         },
#                         {
#                             "color": "#00FF00",
#                             "icon": "undo",
#                             "text": __("delete", {}, lang),
#                             "method": "delete",
#                             "url": "/v1/wb/modules/deleted/" + id
#                         }
#                     ]
#                 }
#             },
#             "redirect_url": "",
#             "request_id": id
#         }
    
# crud = CRUDAPI('Module', 'modules', TBL_MODULE, {})

# def post_module(item:Annotated[ModuleSchema, Body(embed=True)],
# 	current_user: Annotated[User, Depends(get_current_active_user)]
# ):
# 	return crud.post(item.dict(), current_user=current_user)

# def put_module(id,item:Annotated[ModuleSchema, Body(embed=True)],
# 	current_user: Annotated[User, Depends(get_current_active_user)]
# ):
# 	return crud.put(id, item.dict(), current_user=current_user)

# def list_module(page: int, size:int,
# 	current_user: Annotated[User, Depends(get_current_active_user)]
# ):
# 	obj = db.query(TBL_MODULE).with_entities(
# 		TBL_MODULE.id, 
# 		TBL_MODULE.name, 
# 		TBL_MODULE.name_lc, 
# 		TBL_MODULE.re_created_at,
# 		TBL_MODULE.re_created_by,
# 	)
# 	header = [
# 		{'key':'id', 'label':'ID'},
# 		{'key':'name', 'label':'Name'},
# 		{'key':'name_lc', 'label':'Local Name'},
# 		{'key':'re_created_at', 'label':'Created At'},
# 		{'key':'re_created_by', 'label':'Created By'}
# 	]
# 	return crud.list(obj, page, size, header, current_user=current_user)

# def list_history_module(page: int, size:int,
# 	current_user: Annotated[User, Depends(get_current_active_user)]
# ):
# 	return crud.list_history(None, page, size, header, current_user=current_user)

# def list_unauth_module(page: int, size:int,
# 	current_user: Annotated[User, Depends(get_current_active_user)]
# ):
# 	return crud.list_unauth(None, page, size, header, current_user=current_user)

# def list_deleted_module(page: int, size:int,
# 	current_user: Annotated[User, Depends(get_current_active_user)]
# ):
# 	return crud.list_deleted(None, page, size, header, current_user=current_user)

# def post_comment_module(id: str, comment:CommentModuleSchema,
# 	current_user: Annotated[User, Depends(get_current_active_user)]
# ):
# 	return crud.post_comment(id, comment.dict()['comment'], current_user=current_user)

# def update_comment_module(id: str, comment_id, comment:CommentModuleSchema,
# 	current_user: Annotated[User, Depends(get_current_active_user)]
# ):
# 	return crud.update_comment(id, comment_id, comment.dict()['comment'], current_user=current_user)


# crud.router.add_api_route('/{id}/comment/{comment_id}', update_comment_module, methods=['PUT'])
# crud.router.add_api_route('/{id}/comment', post_comment_module, methods=['POST'])
# crud.router.add_api_route('', list_module, methods=['GET'])
# crud.router.add_api_route('/list-history', list_history_module, methods=['GET'])
# crud.router.add_api_route('/list-unauth', list_unauth_module, methods=['GET'])
# crud.router.add_api_route('/list-deleted', list_deleted_module, methods=['GET'])
# crud.router.add_api_route('', post_module, methods=['POST'])
# crud.router.add_api_route('', put_module, methods=['PUT'])
# app.include_router(crud.router, prefix="/api/v1", tags=['Module'])

class MODULE_ACCESSMENT_CRUD_API(CRUDAPI):
    def get_header(self): 
        return [
            {'field': 'id', 'text': 'ID'},
            {'field': 'name', 'text': 'Name'}
        ]
    
    from sqlalchemy import func

    def before_response(self, items, obj=None):
        ids = [item.get('id') for item in items]

        # Query to get sum/count for each parent_id
        results = db.query(
            TBL_MODULE_ACCESSMENT_ITEM.parent_id,
            func.count(TBL_MODULE_ACCESSMENT_ITEM.id).label("total")
        ).filter(
            TBL_MODULE_ACCESSMENT_ITEM.parent_id.in_(ids)
        ).group_by(
            TBL_MODULE_ACCESSMENT_ITEM.parent_id
        ).all()

        modules_count = {parent_id: total for parent_id, total in results}

        for item in items:
            item_id = item.get("id")
            item["module_count"] = modules_count.get(item_id, 0)

        return items

    def get_header_sub(self): 
        return {
            'module_accessment_items': [
                {'field': 'id', 'text': 'ID'},
                {'field': 'module_id', 'text': 'Module ID'},
                {'field': 'num_of_record', 'text': 'Number of Record'},
            ]
        }
    
    def get_vsi_query(self, record_type=''):
        model_1 = getattr(self.moduleList, str(self.sub_models.get('module_accessment_items').__name__) + record_type)

        q1 = db.query(model_1)

        return {'module_accessment_items': q1}
    
crud = MODULE_ACCESSMENT_CRUD_API(
    'ModuleAccessment', 
    'module-accessment', 
    TBL_MODULE_ACCESSMENT, 
    {
        'module_accessment_items': TBL_MODULE_ACCESSMENT_ITEM,
    }, 
    schema=ModuleAccessmentSchema, 
    sub_schema=ModuleAccessmentSubListSchema, 
)
crud.init_route()
app.include_router(crud.router, prefix='/api/v1', tags=['Module'])

class MODULE_ASSIGNMENT_CRUD_API(CRUDAPI): 
    def get_header(self): 
        return [
            {'field': 'id', 'text': 'ID'},
            {'field': 'module_accessment_id', 'text': 'Module Accessment ID'},
            {'field': 'assigned_company_id', 'text': 'Assigned Company ID'},
        ]

crud = MODULE_ASSIGNMENT_CRUD_API(
    'ModuleAssignment', 
    'module-assignment', 
    TBL_MODULE_ASSIGNMENT, 
    {}, 
    schema=ModuleAssignmentSchema,
)
crud.init_route()
app.include_router(crud.router, prefix='/api/v1', tags=['Module'])

@app.get('/api/v1/get-user-access-module', tags=['Module'])
def get_user_access_module(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db          : Session = Depends(get_db),
    page        : int = 1, 
    size        : int = 10, 
):
    m_query = db.query(TBL_MODULE_ASSIGNMENT).filter(TBL_MODULE_ASSIGNMENT.assigned_company_id == current_user.token_working_company_id).first()
    
    if not m_query: 
        m_query = db.query(TBL_MODULE)

        total = m_query.count()
        data = m_query.limit(size).offset((page - 1) * size).all()
        
        return ResponseModel(
            status=True,
            title='User Access Module', 
            message='Data retrieved successfully',
            data={
                'lists': data,     
                'meta_data': {
                    'total': total, 
                    'total_page': math.ceil(total / size), 
                    'current_page': page, 
                    'size': size, 
                },
            },
            error='',
        )
    
    if core_lib.check_is_superuser(db, current_user):
        m_query = db.query(TBL_MODULE).\
            outerjoin(TBL_MODULE_ACCESSMENT_ITEM, TBL_MODULE_ACCESSMENT_ITEM.module_id == TBL_MODULE.id).\
            outerjoin(TBL_MODULE_ACCESSMENT, TBL_MODULE_ACCESSMENT.id == TBL_MODULE_ACCESSMENT_ITEM.parent_id).\
            outerjoin(TBL_MODULE_ASSIGNMENT, TBL_MODULE_ASSIGNMENT.module_accessment_id == TBL_MODULE_ACCESSMENT.id).\
            filter(
                TBL_MODULE_ASSIGNMENT.assigned_company_id == current_user.token_working_company_id
            )
        
        total = m_query.count()
        data = m_query.limit(page).offset((page - 1) * size).all()
        
        return ResponseModel(
            status=True,
            title='User Access Module', 
            message='Data retrieved successfully',
            data={
                'lists': data,     
                'meta_data': {
                    'total': total, 
                    'total_page': math.ceil(total / size), 
                    'current_page': page, 
                    'size': size, 
                }
            },
            error='',
        )
    
    m_query = db.query(TBL_ROLE_MODULE, TBL_MODULE).\
        outerjoin(TBL_ROLE, TBL_ROLE.id == TBL_ROLE_MODULE.parent_id).\
        outerjoin(TBL_USER_LOCATION_ASSIGNMENT, TBL_USER_LOCATION_ASSIGNMENT.role_id == TBL_ROLE.id).\
        outerjoin(TBL_MODULE, TBL_MODULE.id == TBL_ROLE_MODULE.module_id).\
        filter(
            TBL_USER_LOCATION_ASSIGNMENT.user_id == current_user.id,
            TBL_USER_LOCATION_ASSIGNMENT.accessible_company_id == current_user.token_working_company_id,
            TBL_ROLE.is_superuser == False,
        )
    
    total = m_query.count()
    data = m_query.limit(size).offset((page - 1) * size).all()
    
    return ResponseModel(
        status=True,
        title='User Access Module', 
        message='Data retrieved successfully',
        data={
            'lists': data,     
            'meta_data': {
                'total': total, 
                'total_page': math.ceil(total / size), 
                'current_page': page, 
                'size': size, 
            }
        },
        error='',
    )

@app.get('/api/v1/get-system-modules', tags=['Module'])
def get_system_modules(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    # Only superuser can access
    if not check_is_superuser(db, current_user):
        raise HTTPException(status_code=403, detail="Permission denied")

    all_cruds_data = []
    base_dir = os.path.join(os.path.dirname(__file__), "api")  # adjust if needed
    print('======> Base Dir : ', base_dir)
    base_package = "api"

    for root, dirs, files in os.walk(base_dir):
        print('======> Root : ', root)
        print('======> Dirs : ', dirs)
        print('======> Files : ', files)
        
        for file in files:
            print('======> Files : ', file)
            if file == "view.py":
                # Compute module path for import
                rel_path = os.path.relpath(root, os.path.dirname(__file__))  # relative path
                module_path = rel_path.replace(os.sep, ".") + ".view"
                module_path = module_path.replace("..", base_package)  # fix path if needed
                try:
                    module = importlib.import_module(module_path)
                    if hasattr(module, "crud"):
                        crud_instance = getattr(module, "crud")
                        all_cruds_data.append({
                            "module_name": getattr(crud_instance, "model_name", None),
                            "prefix": getattr(crud_instance.router, "prefix", None),
                            "tags": getattr(crud_instance.router, "tags", []),
                            "routes": [route.path for route in crud_instance.router.routes],
                        })
                except Exception as e:
                    print(f"Failed to import {module_path}: {e}")

    return ResponseModel(
        status=True,
        title='System Modules',
        message='Data retrieved successfully',
        data={'lists': all_cruds_data},
        error='',
    )