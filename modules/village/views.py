from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from icb.lib.join_helper import JoinHelper
from modules.commune.models import TBL_COMMUNE
from modules.location_join import prefixed_id_join
from modules.location_id import assign_prefixed_id
from modules.new_route import empty_new_response

class VILLAGE_CRUD(CRUDAPI):
    query_fields = ['name']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_VILLAGE,
            TBL_VILLAGE_UNAUTH,
            TBL_VILLAGE_HISTORY,
            TBL_VILLAGE_DELETED,
            TBL_VILLAGE_REJECTED,
        ], "VL")
        return True, ''

    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "name", "text" : "Name"},
            {"field" : "name_lc", "text" : "Name(Local)"},
            {"field" : "commune_id", "text" : "Commune ID"},
            {"field" : "name", "model": TBL_COMMUNE, "label": "commune_name", "text" : "Commune"},
            {"field" : "description", "text" : "Description"},
            {"field" : "image", "text" : "Image"},
            {"label" : "image_link", "concat": [{'field': 'image', 'separator': "" }], "text": "Image Link"},
        ]

    def get_list_query(self, model):
        return(JoinHelper(self.db, model)\
            .outerjoin(TBL_COMMUNE, prefixed_id_join(TBL_COMMUNE.id, model.commune_id, "COM"))\
            .get_query())

crud = VILLAGE_CRUD('Village', 'villages', TBL_VILLAGE, {}, schema=VillageSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Village'])

@app.get("/api/v1/wb/villages/new", tags=["Village"])
async def new_village():
    return empty_new_response("Village")
