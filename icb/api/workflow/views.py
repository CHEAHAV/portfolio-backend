from icb.core.crud_api import CRUDAPI
from icb.api.module.models import TBL_MODULE
from icb.api.role.models import TBL_ROLE
from .schemas import WorkflowSchema, WorkflowListSchema
from .models import *
from main import app


class WORKFLOW_CRUD_API(CRUDAPI):
    query_fields = ['description']

    def get_header(self):
        return [
            {"field": "id", "text": "ID"},
            {"field": "module_id", "text": "Module ID"},
            {"field": "name", "model": TBL_MODULE, "label": "module_name", "text": "Module Name"},
            {"field": "condition", "text": "Condition"},
            {"field": "description", "text": "Description"},
        ]
    
    def get_list_query(self, model):
        return self.db.query(model).outerjoin(TBL_MODULE, TBL_MODULE.id == model.module_id)

    def get_header_sub(self):
        return {
            'detail': [
                {"field": "id", "text": "ID"},
                {"field": "role_id", "text": "Role ID"},
                {"field": "num_of_auth", "text": "Number Of Authorization"},
                {"field": "auth_order", "text": "Authorize Order"},
                {"field": "auth_status", "text": "Authorize Status"},
                {"field": "role_condition", "text": "Condition"},
            ]
        }
    
    def get_vsi_query(self, record_type=''):
        model = getattr(self.moduleList, str(self.sub_models['detail'].__name__) + record_type)
        query = self.db.query(model).outerjoin(TBL_ROLE, TBL_ROLE.id == model.role_id)
        return { 'detail': query }

crud = WORKFLOW_CRUD_API('Workflow','workflows', TBL_WORKFLOW, 
    {'detail' : TBL_WORKFLOW_DETAIL}, 
    schema=WorkflowSchema, 
    sub_schema=WorkflowListSchema
)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Workflow'])
