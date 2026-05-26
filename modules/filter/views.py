from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from modules.location_id import assign_prefixed_id

class FILTER_CRUD(CRUDAPI):
    query_fields = ['name']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_FILTER,
            TBL_FILTER_UNAUTH,
            TBL_FILTER_HISTORY,
            TBL_FILTER_DELETED,
            TBL_FILTER_REJECTED,
        ], "FIL")
        return True, ''

    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "name", "text" : "Name"},
            {"field" : "active", "text" : "Active"},
        ]

crud = FILTER_CRUD('Filter', 'filters', TBL_FILTER, {}, schema=FilterSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Filter'])
