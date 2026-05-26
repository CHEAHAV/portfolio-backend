from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from modules.location_id import assign_prefixed_id

class CAREER_CRUD(CRUDAPI):
    query_fields = ['title']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_CAREER,
            TBL_CAREER_UNAUTH,
            TBL_CAREER_HISTORY,
            TBL_CAREER_DELETED,
            TBL_CAREER_REJECTED,
        ], "CAR")
        return True, ''

    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "title", "text" : "Title"},
            {"field" : "sub_title", "text" : "Sub Title"},
            {"field" : "description", "text" : "Decription"},
            {"field" : "date", "text" : "Date"},
            {"field" : "active", "text" : "Active"},
        ]

crud = CAREER_CRUD('Career', 'careers', TBL_CAREER, {}, schema=CareerSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Career'])
