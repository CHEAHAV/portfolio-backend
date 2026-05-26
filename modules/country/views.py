from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from modules.location_id import assign_prefixed_id
from modules.new_route import empty_new_response

class COUNTRY_CRUD(CRUDAPI):
    query_fields = ['name']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_COUNTRY,
            TBL_COUNTRY_UNAUTH,
            TBL_COUNTRY_HISTORY,
            TBL_COUNTRY_DELETED,
            TBL_COUNTRY_REJECTED,
        ], "CO")
        return True, ''

    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "name", "text" : "Name"},
            {"field" : "name_lc", "text" : "Name(Local)"},
            {"field" : "description", "text" : "Description"},
            {"field" : "image", "text" : "Image"},
            {"label" : "image_link", "concat": [{'field': 'image', 'separator': f"{os.getenv('APP_URL','')}/static/images/Country/" }], "text": "Image Link"},
        ]

crud = COUNTRY_CRUD('Country', 'countries', TBL_COUNTRY, {}, schema=CountrySchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Country'])

@app.get("/api/v1/wb/countries/new", tags=["Country"])
async def new_country():
    return empty_new_response("Country")
