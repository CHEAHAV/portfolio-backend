from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from modules.location_id import assign_prefixed_id

class STUDY_CRUD(CRUDAPI):
    query_fields = ['title']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_STUDY,
            TBL_STUDY_UNAUTH,
            TBL_STUDY_HISTORY,
            TBL_STUDY_DELETED,
            TBL_STUDY_REJECTED,
        ], "STD")
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

crud = STUDY_CRUD('Study', 'studies', TBL_STUDY, {}, schema=StudySchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Study'])
