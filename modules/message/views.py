from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from modules.location_id import assign_prefixed_id

class MESSAGE_CRUD(CRUDAPI):
    query_fields = ['id']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_MESSAGE,
            TBL_MESSAGE_UNAUTH,
            TBL_MESSAGE_HISTORY,
            TBL_MESSAGE_DELETED,
            TBL_MESSAGE_REJECTED,
        ], "MES")
        return True, ''
    
    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "first_name", "text" : "First Name"},
            {"field" : "last_name", "text" : "Last Name"},
            {"field" : "email", "text" : "Email"},
            {"field" : "subject", "text" : "Subject"},
            {"field" : "message", "text" : "Message"},
            {"field" : "active", "text" : "Active"},
        ]
    
crud = MESSAGE_CRUD('Message', 'messages', TBL_MESSAGE, {}, schema = MessageSchemas)
crud.init_route()
app.include_router(crud.router, prefix = "/api/v1", tags = ['Message'])