from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from modules.location_id import assign_prefixed_id

class SKILL_CRUD(CRUDAPI):
    query_fields = ['name']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_SKILL,
            TBL_SKILL_UNAUTH,
            TBL_SKILL_HISTORY,
            TBL_SKILL_DELETED,
            TBL_SKILL_REJECTED,
        ], "SKI")
        return True, ''

    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "name", "text" : "Name"},
            {"field" : "score", "text" : "Score"},
            {"field" : "description", "text" : "Decription"},
            {"field" : "image", "text" : "Image"},
            {"label" : "image_link", "concat": [{'field': 'image', 'separator': f"{os.getenv('APP_URL','')}/static/images/Skill/" }], "text": "Image Link"},
            {"field" : "active", "text" : "Active"},
        ]

crud = SKILL_CRUD('Skill', 'skills', TBL_SKILL, {}, schema=SkillSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Skill'])
