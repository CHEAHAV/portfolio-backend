from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *

class GENDER_CRUDAPI(CRUDAPI):
  query_fields = ['description', 'description_lc']
  
  def get_header(self):
    return [
        {"field": "id", "text": "ID"},
        {"field": "description", "text": "Description"},
        {"field": "description_lc", "text": "Description (Local)"},
        {"field": "order", "text": "Order"},
        {"field": "icon", "text": "Icon"},
      ]

crud = GENDER_CRUDAPI('Gender', 'genders', TBL_GENDER, {}, schema=GenderSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Gender'])
