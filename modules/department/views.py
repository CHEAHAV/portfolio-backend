from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from modules.location_id import assign_prefixed_id
from modules.new_route import empty_new_response

class DEPARTMENT_CRUD(CRUDAPI):
    query_fields = ['name']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_DEPARTMENT,
            TBL_DEPARTMENT_UNAUTH,
            TBL_DEPARTMENT_HISTORY,
            TBL_DEPARTMENT_DELETED,
            TBL_DEPARTMENT_REJECTED,
        ], "DEP")
        return True, ''

    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "name", "text" : "Name"},
            {"field" : "description", "text" : "Description"},
            {"field" : "image", "text" : "Image"},
            {"label" : "image_link", "concat": [{'field': 'image', 'separator': "" }], "text": "Image Link"},
            {"field" : "active", "text" : "Active"},
        ]

@app.get("/api/v1/wb/departments/new", tags=["Department"])
async def new_department():
    return empty_new_response("Department")

crud = DEPARTMENT_CRUD('Department', 'departments', TBL_DEPARTMENT, {}, schema=DepartmentSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Department'])
