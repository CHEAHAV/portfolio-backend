from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from modules.location_id import assign_prefixed_id

class SOCIAL_CRUD(CRUDAPI):
    query_fields = ['name']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_SOCIAL,
            TBL_SOCIAL_UNAUTH,
            TBL_SOCIAL_HISTORY,
            TBL_SOCIAL_DELETED,
            TBL_SOCIAL_REJECTED,
        ], "SOC")
        return True, ''

    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "name", "text" : "Name"},
            {"field" : "icon", "text" : "Icon"},
            {"label" : "icon_link", "concat": [{'field': 'icon', 'separator': f"{os.getenv('APP_URL','')}/static/images/ContactMe/" }], "text": "Icon Link"},
            {"field" : "active", "text" : "Active"},
        ]

crud = SOCIAL_CRUD('Social', 'socials', TBL_SOCIAL, {}, schema=SocialSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Social'])
