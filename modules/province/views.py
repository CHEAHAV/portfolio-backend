from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from modules.country.models import TBL_COUNTRY
from icb.lib.join_helper import JoinHelper
from modules.location_join import prefixed_id_join
from modules.location_id import assign_prefixed_id
from modules.new_route import empty_new_response

class PROVINCE_CRUD(CRUDAPI):
    query_fields = ['name']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_PROVINCE,
            TBL_PROVINCE_UNAUTH,
            TBL_PROVINCE_HISTORY,
            TBL_PROVINCE_DELETED,
            TBL_PROVINCE_REJECTED,
        ], "PRO")
        return True, ''

    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "name", "text" : "Name"},
            {"field" : "name_lc", "text" : "Name(Local)"},
            {"field" : "country_id", "text" : "Country ID"},
            {"field" : "name", "model": TBL_COUNTRY, "label": "country_name", "text" : "Country"},
            {"field" : "description", "text" : "Description"},
            {"field" : "image", "text" : "Image"},
            {"label" : "image_link", "concat": [{'field': 'image', 'separator': "" }], "text": "Image Link"},
        ]

    def get_list_query(self, model):
        return(JoinHelper(self.db, model)\
            .outerjoin(TBL_COUNTRY, prefixed_id_join(TBL_COUNTRY.id, model.country_id, "COU"))\
            .get_query())

crud = PROVINCE_CRUD('Province', 'provinces', TBL_PROVINCE, {}, schema=ProvinceSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Province'])

@app.get("/api/v1/wb/provinces/new", tags=["Province"])
async def new_province():
    return empty_new_response("Province")
