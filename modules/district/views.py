from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from icb.lib.join_helper import JoinHelper
from modules.province.models import TBL_PROVINCE
from modules.location_join import prefixed_id_join
from modules.location_id import assign_prefixed_id
from modules.new_route import empty_new_response

class DISTRICT_CRUD(CRUDAPI):
    query_fields = ['name']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_DISTRICT,
            TBL_DISTRICT_UNAUTH,
            TBL_DISTRICT_HISTORY,
            TBL_DISTRICT_DELETED,
            TBL_DISTRICT_REJECTED,
        ], "DIS")
        return True, ''

    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "name", "text" : "Name"},
            {"field" : "name_lc", "text" : "Name(Local)"},
            {"field" : "province_id", "text" : "Province ID"},
            {"field" : "name", "model": TBL_PROVINCE, "label": "province_name", "text" : "Province"},
            {"field" : "description", "text" : "Description"},
            {"field" : "image", "text" : "Image"},
            {"label" : "image_link", "concat": [{'field': 'image', 'separator': f"{os.getenv('APP_URL','')}/static/images/District/" }], "text": "Image Link"},
        ]

    def get_list_query(self, model):
        return(JoinHelper(self.db, model)\
            .outerjoin(TBL_PROVINCE, prefixed_id_join(TBL_PROVINCE.id, model.province_id, "PRO"))\
            .get_query())

crud = DISTRICT_CRUD('District', 'districts', TBL_DISTRICT, {}, schema=DistrictSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['District'])

@app.get("/api/v1/wb/districts/new", tags=["District"])
async def new_district():
    return empty_new_response("District")
