from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from icb.api.module.models import TBL_MODULE
from icb.api.user.models import TBL_USER
from modules.location_id import assign_prefixed_id

class CUSTOM_CRUDAPI(CRUDAPI):
    def before_save(self):
        assign_prefixed_id(self, [
            TBL_RESET_ATTEMPT,
            TBL_RESET_ATTEMPT_UNAUTH,
            TBL_RESET_ATTEMPT_HISTORY,
            TBL_RESET_ATTEMPT_DELETED,
            TBL_RESET_ATTEMPT_REJECTED,
        ], "RSA")
        return True, ''

    def get_header(self):
        return [
            {"field": "id", "text": "ID"},
            {"field": "user_id", "text": "User ID"},
            {"field": "", "concat":[
                { "field":"first_name", "model": TBL_USER},
                { "field":"last_name", "model": TBL_USER}
            ], "label": "user_name", "text": "Name"},
            {"field": "username", "model": TBL_USER, "label": "username", "text": "Username"},
            {"field": "email", "model": TBL_USER, "label": "email", "text": "Email"},
            {"field": "phone", "model": TBL_USER, "label": "phone", "text": "Phone"},
            {"field": "note", "text": "Note"},
        ]
    
    def get_list_query(self, model):
        return self.db.query(model).\
            outerjoin(TBL_USER, TBL_USER.id==model.user_id)
    
    def after_save(self):
        module = self.db.query(TBL_MODULE).filter(TBL_MODULE.name == 'ResetAttempt').first()
        if module is None or module.num_of_auth == 0:
            user = self.db.query(TBL_USER).filter(TBL_USER.id == self.item['user_id']).first()
            if user:
                user.attempt = 0
                self.db.add(user)
            
        return True, ''
    
    def after_approve(self):
        user = self.db.query(TBL_USER).filter(TBL_USER.id == self.cObj.user_id).first()
        if user:
            user.attempt = 0
            self.db.add(user)
        
        return True, ''
    
crud = CUSTOM_CRUDAPI('ResetAttempt', 'reset-attempt', TBL_RESET_ATTEMPT, {}, schema=ResetAttemptSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Reset Attempt'])
