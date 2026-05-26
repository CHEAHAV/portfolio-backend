from modules.color.models import *
from modules.color.schemas import ColorSchema
from core.crud_api import CRUDAPI
from main import app


class COLOR_CRUD_API(CRUDAPI):
    # query_fields = ['id','name']
    def get_header(self):
        return [
            {"field": "id", "text": "ID"},
            {"field": "name", "text": "Color Name"},
        ]
    
crud = COLOR_CRUD_API('Color', 'colors', TBL_COLOR, {}, schema=ColorSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Color'])