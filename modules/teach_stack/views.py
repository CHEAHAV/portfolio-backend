from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from modules.location_id import assign_prefixed_id

class TEACH_STACK_CRUD(CRUDAPI):
    query_fields = ['name']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_TEACH_STACK,
            TBL_TEACH_STACK_UNAUTH,
            TBL_TEACH_STACK_HISTORY,
            TBL_TEACH_STACK_DELETED,
            TBL_TEACH_STACK_REJECTED,
        ], "TST")
        return True, ''

    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "name_left", "text" : "Name Left"},
            {"field" : "image_left", "text" : "Image Left"},
            {"label" : "image_left_link", "concat": [{'field': 'image_left', 'separator': f"{os.getenv('APP_URL','')}/static/images/TeachStack/" }], "text": "Image Left Link"},
            {"field" : "name_right", "text" : "Name Right"},
            {"field" : "image_right", "text" : "Image Right"},
            {"label" : "image_right_link", "concat": [{'field': 'image_right', 'separator': f"{os.getenv('APP_URL','')}/static/images/TeachStack/" }], "text": "Image Right Link"},
            {"field" : "active", "text" : "Active"},
        ]

crud = TEACH_STACK_CRUD('TeachStack', 'teach-stacks', TBL_TEACH_STACK, {}, schema=TeachStackSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['TeachStack'])
