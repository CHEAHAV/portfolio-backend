from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from modules.location_id import assign_prefixed_id

class CONTACT_ME_CRUD(CRUDAPI):
    query_fields = ['name']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_CONTACT_ME,
            TBL_CONTACT_ME_UNAUTH,
            TBL_CONTACT_ME_HISTORY,
            TBL_CONTACT_ME_DELETED,
            TBL_CONTACT_ME_REJECTED,
        ], "CON")
        return True, ''

    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "name", "text" : "Name"},
            {"field" : "description", "text" : "Description"},
            {"field" : "icon", "text" : "Icon"},
            {"label" : "icon_link", "concat": [{'field': 'icon', 'separator': "" }], "text": "Icon Link"},
            {"field" : "active", "text" : "Active"},
        ]

crud = CONTACT_ME_CRUD('ContactMe', 'contact-mes', TBL_CONTACT_ME, {}, schema=ContactMeSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['ContactMe'])
