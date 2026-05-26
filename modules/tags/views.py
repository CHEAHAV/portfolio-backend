from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *

class TAGS_CRUD(CRUDAPI):
    query_fields = ['name']

    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "name", "text" : "Name"},
            {"field" : "description", "text" : "Description"},
            {"field" : "active", "text" : "Active"},
        ]

crud = TAGS_CRUD('Tags', 'tags', TBL_TAGS, {}, schema=TagsSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Tags'])