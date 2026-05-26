from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from modules.location_id import assign_prefixed_id

class STORY_CRUD(CRUDAPI):
    query_fields = ['name']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_STORY,
            TBL_STORY_UNAUTH,
            TBL_STORY_HISTORY,
            TBL_STORY_DELETED,
            TBL_STORY_REJECTED,
        ], "STO")
        return True, ''

    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "title", "text" : "Title"},
            {"field" : "description", "text" : "Description"},
            {"field" : "icon_name", "text" : "Icon name"},
            {"field" : "icon", "text" : "Icon"},
            {"label" : "icon_link", "concat": [{'field': 'icon', 'separator': f"{os.getenv('APP_URL','')}/static/images/ContactMe/" }], "text": "Icon Link"},
            {"field" : "active", "text" : "Active"},
        ]

crud = STORY_CRUD('Story', 'stories', TBL_STORY, {}, schema=StorySchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Story'])
