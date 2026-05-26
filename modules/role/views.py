from main import app, Body
from icb.core.crud_api import *
from icb.api.role.models import (
    TBL_ROLE,
    TBL_ROLE_DELETED,
    TBL_ROLE_HISTORY,
    TBL_ROLE_MODULE,
    TBL_ROLE_REJECTED,
    TBL_ROLE_UNAUTH,
)
from .schemas import *
from modules.location_id import assign_prefixed_id


class CUSTOM_CRUDAPI(CRUDAPI):
    query_fields = ['name']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_ROLE,
            TBL_ROLE_UNAUTH,
            TBL_ROLE_HISTORY,
            TBL_ROLE_DELETED,
            TBL_ROLE_REJECTED,
        ], "ROL")
        return True, ''

    def get_header(self):
        return [
            {"field": "id", "text": "ID", "width": "20%", "align": "center", "sortable": True, "searchable": True},
            {"field": "name", "text": "Name", "width": "30%", "align": "left", "sortable": False, "searchable": True},
            {"field": "name_lc", "text": "Name (Local)"},
            {"field": "is_superuser", "text": "Super User"},
        ]

crud = CUSTOM_CRUDAPI('Role','roles', TBL_ROLE,{'sub_item':TBL_ROLE_MODULE}, schema=RoleSchema, sub_schema=RoleModuleListSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Role'])
