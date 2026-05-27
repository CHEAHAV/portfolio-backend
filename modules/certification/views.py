from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from modules.location_id import assign_prefixed_id

class CERTIFICATION_CRUD(CRUDAPI):
    query_fields = ['name']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_CERTIFICATION,
            TBL_CERTIFICATION_UNAUTH,
            TBL_CERTIFICATION_HISTORY,
            TBL_CERTIFICATION_DELETED,
            TBL_CERTIFICATION_REJECTED,
        ], "CER")
        return True, ''

    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "name", "text" : "Name"},
            {"field" : "title", "text" : "Title"},
            {"field" : "issuer", "text" : "Issuer"},
            {"field" : "date_earned", "text" : "Date Earned"},
            {"field" : "credential_id", "text" : "Credential ID"},
            {"field" : "icon", "text" : "Icon"},
            {"label" : "icon_link", "concat": [{'field': 'icon', 'separator': "" }], "text": "Icon Link"},
            {"field" : "active", "text" : "Active"},
        ]

crud = CERTIFICATION_CRUD('Certification', 'certifications', TBL_CERTIFICATION, {}, schema=CertificationSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Certification'])
