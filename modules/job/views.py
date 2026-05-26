from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from icb.lib.join_helper import JoinHelper
from modules.department.models import TBL_DEPARTMENT
from modules.province.models import TBL_PROVINCE
from modules.district.models import TBL_DISTRICT
from modules.commune.models import TBL_COMMUNE
from modules.village.models import TBL_VILLAGE
from modules.location_id import assign_prefixed_id
from modules.location_join import lookup_name, prefixed_id_join

def get_name(db, model, id):
    return lookup_name(db, model, id)


class JOB_CRUDAPI(CRUDAPI):
    query_fields = ['title']

    def before_save(self):
        assign_prefixed_id(self, [
            TBL_JOB,
            TBL_JOB_UNAUTH,
            TBL_JOB_HISTORY,
            TBL_JOB_DELETED,
            TBL_JOB_REJECTED,
        ], "JOB")
        return True, ''

    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "title", "text" : "Title"},
            {"field" : "department_id", "text" : "Department ID"},
            {"field" : "name", "model": TBL_DEPARTMENT, "label": "department_name", "text" : "Department"},
            {"field" : "province_id", "text" : "Province ID"},
            {"field" : "name", "model": TBL_PROVINCE, "label": "province_name", "text" : "Province"},
            {"field" : "district_id", "text" : "District ID"},
            {"field" : "name", "model": TBL_DISTRICT, "label": "district_name", "text" : "District"},
            {"field" : "commune_id", "text" : "Commune ID"},
            {"field" : "name", "model": TBL_COMMUNE, "label": "commune_name", "text" : "Commune"},
            {"field" : "village_id", "text" : "Village ID"},
            {"field" : "name", "model": TBL_VILLAGE, "label": "village_name", "text" : "Village"},
            {"field" : "employment_type", "text" : "Employment Type"},
            {"field" : "position_available", "text" : "Position Available"},
            {"field" : "salary_range", "text" : "Salary Range"},
            {"field" : "work_start_time", "text" : "Work Start Time"},
            {"field" : "work_end_time", "text" : "Work End Time"},
            {"field" : "urgent_flag", "text" : "Urgent Flag"},
            {"field" : "role", "text" : "Role"},
            {"field" : "responsibilities", "text" : "Responsibilities"},
            {"field" : "qualifications", "text" : "Qualifications"},
            {"field" : "status", "text" : "Status"},
            {"field" : "order", "text" : "Order"},
            {"field" : "active", "text" : "Active"},
        ]
    
    def get_list_query(self, model):
        return(JoinHelper(self.db, model)\
            .outerjoin(TBL_DEPARTMENT, TBL_DEPARTMENT.id == model.department_id)\
            .outerjoin(TBL_PROVINCE, prefixed_id_join(TBL_PROVINCE.id, model.province_id, "PRO"))\
            .outerjoin(TBL_DISTRICT, prefixed_id_join(TBL_DISTRICT.id, model.district_id, "DIS"))\
            .outerjoin(TBL_COMMUNE, prefixed_id_join(TBL_COMMUNE.id, model.commune_id, "COM"))\
            .outerjoin(TBL_VILLAGE, prefixed_id_join(TBL_VILLAGE.id, model.village_id, "VL"))\
            .get_query())

    def before_view_response(self, item):
        data = item.get("item", item) if isinstance(item, dict) else {}
        if isinstance(data, dict) and "data" in data:
            data = data.get("data", {}).get("item", data)
        if not isinstance(data, dict):
            return item

        data["department_name"] = get_name(self.db, TBL_DEPARTMENT, data.get("department_id"))
        data["province_name"] = lookup_name(self.db, TBL_PROVINCE, data.get("province_id"), "PRO")
        data["district_name"] = lookup_name(self.db, TBL_DISTRICT, data.get("district_id"), "DIS")
        data["commune_name"] = lookup_name(self.db, TBL_COMMUNE, data.get("commune_id"), "COM")
        data["village_name"] = lookup_name(self.db, TBL_VILLAGE, data.get("village_id"), "VL")

        return item
    
crud = JOB_CRUDAPI('Job', 'jobs', TBL_JOB, {}, schema=JobSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Job'])
