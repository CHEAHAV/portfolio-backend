from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from modules.location_id import assign_prefixed_id

class PROJECT_CRUD(CRUDAPI):
    query_fields = ['name']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_PROJECT,
            TBL_PROJECT_UNAUTH,
            TBL_PROJECT_HISTORY,
            TBL_PROJECT_DELETED,
            TBL_PROJECT_REJECTED,
        ], "PRO")
        return True, ''

    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "name", "text" : "Name"},
            {"field" : "description", "text" : "Decription"},
            {"field" : "duration", "text" : "Duration"},
            {"field" : "role", "text" : "Role"},
            {"field" : "platform", "text" : "Platform"},
            {"field" : "challenge", "text" : "Challenge"},
            {"field" : "image", "text" : "Image"},
            {"label" : "image_link", "concat": [{'field': 'image', 'separator': "" }], "text": "Image Link"},
            {"field" : "active", "text" : "Active"},
        ]

crud = PROJECT_CRUD('Project', 'projects', TBL_PROJECT, {}, schema=ProjectSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Project'])
