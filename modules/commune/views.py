from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from icb.lib.join_helper import JoinHelper
from modules.district.models import TBL_DISTRICT
from modules.location_join import prefixed_id_join
from modules.location_id import assign_prefixed_id
from modules.new_route import empty_new_response

class COMMUNE_CRUD(CRUDAPI):
    query_fields = ['name']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_COMMUNE,
            TBL_COMMUNE_UNAUTH,
            TBL_COMMUNE_HISTORY,
            TBL_COMMUNE_DELETED,
            TBL_COMMUNE_REJECTED,
        ], "COM")
        return True, ''

    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "name", "text" : "Name"},
            {"field" : "name_lc", "text" : "Name(Local)"},
            {"field" : "district_id", "text" : "District ID"},
            {"field" : "name", "model": TBL_DISTRICT, "label": "district_name", "text" : "District"},
            {"field" : "description", "text" : "Description"},
            {"field" : "image", "text" : "Image"},
            {"label" : "image_link", "concat": [{'field': 'image', 'separator': "" }], "text": "Image Link"},
        ]

    def get_list_query(self, model):
        return(JoinHelper(self.db, model)\
            .outerjoin(TBL_DISTRICT, prefixed_id_join(TBL_DISTRICT.id, model.district_id, "DIS"))\
            .get_query())

crud = COMMUNE_CRUD('Commune', 'communes', TBL_COMMUNE, {}, schema=CommuneSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Commune'])

@app.get("/api/v1/wb/communes/new", tags=["Commune"])
async def new_commune():
    return empty_new_response("Commune")
