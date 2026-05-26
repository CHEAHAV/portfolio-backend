from main 				import app
from icb.core.crud_api  import CRUDAPI
from .models 			import *
from .schemas 			import *

class CUSTOM_CRUDAPI(CRUDAPI):
    query_fields = ['description']
    list_all = True
    def get_header(self):
        return [
                {"field": "id", "text": "ID", "width": "20%", "align": "center", "sortable": True, "searchable": True},
                {"field": "description", "text": "Description", "width": "30%", "align": "left", "sortable": False, "searchable": True},
                {"field": "description_lc", "text": "Description(Local)", "width": "30%", "align": "left", "sortable": False, "searchable": True},
            ]



crud = CUSTOM_CRUDAPI('Gender', 'genders', TBL_GENDER, {}, schema=GenderSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Gender'])
