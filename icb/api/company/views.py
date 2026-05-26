import os

from fastapi import Query

# from icb.lib.utils import customFilter, customFilterWithCustomFields
from icb.lib.utils import customFilter, customFilterWithCustomFields
from main import app
from icb.core.crud_api import * 
from .models import *
from .schemas import *
# from ..company.models import TBL_COMPANY
# from ..country.models import TBL_COUNTRY
# from ..province.models import TBL_PROVINCE
# from ..district.models import TBL_DISTRICT
# from ..commune.models import TBL_COMMUNE
# from ..village.models import TBL_VILLAGE
from ..branch.models import *
from icb.core.lib import check_is_superuser, get_lang
from ..system_setting.models import *
from ..role.models import TBL_ROLE
from ..user.models import TBL_USER_LOCATION_ASSIGNMENT
import icb.core.lib as core_lib
from icb.lib.join_helper import JoinHelper
from icb.core.lib import check_is_superuser

class COMPANY_CRUD_API(CRUDAPI):
    query_fields = ['name']
    
    
    def get_header(self):
        return [
			{"field": "id", "text": "ID"},
			{"field": "name", "text": "Company Name"},
			{"field": "name_lc", "text": "Company Name (Local)"},
			{"field": "description", "text": "Description"},
			{"field": "description_lc", "text": "Description (Local)"},
			{"field": "logo", "text": "Logo"},
      		{"label": "logo_link", "concat": [{'field': 'logo', 'separator': f"{os.getenv('APP_URL','')}/static/images/Company/" }], "text": "Logo Link"},
			{"field": "banner", "text": "Banner"},
      		{"label": "banner_link", "concat": [{'field': 'banner', 'separator': f"{os.getenv('APP_URL','')}/static/images/Company/" }], "text": "Banner Link"},
			{"field": "phone", "text": "Phone"},
			{"field": "phone_2", "text": "Secondary Phone"},
			{"field": "telegram", "text": "Telegram"},
			{"field": "email", "text": "Email"},
			{"field": "website", "text": "Website"},
			{"field": "facebook", "text": "Facebook"},
			{"field": "youtube", "text": "YouTube"},
			# {"field": "country_id", "text": "Country"},
   			# {"field": "name", "text": "Country", "model": TBL_COUNTRY, "label": "country_name"},
			# {"field": "province_id", "text": "Province"},
			# {"field": "name", "text": "Province",  "model": TBL_PROVINCE, "label": "province_name"},
			# {"field": "district_id", "text": "District"},
			# {"field": "name", "text": "District", "model": TBL_DISTRICT, "label": "district_name"},
			# {"field": "commune_id", "text": "Commune"},
			# {"field": "name", "text": "Commune", "model": TBL_COMMUNE, "label": "commune_name"},
			# {"field": "village_id", "text": "Village"},
			# {"field": "name", "text": "Village", "model": TBL_VILLAGE, "label": "village_name"},
			{"field": "street_no", "text": "Street No."},
			{"field": "house_no", "text": "House No."},
			{'field': 'lat_long', 'text': 'Latitude/Longitude'},
			{"field": "registration_number", "text": "Registration No."},
			{"field": "parent_company_id", "text": "Parent Company ID"},
			{"field": "vat_tin", "text": "VAT TIN"},
		]
    
    def get_list_query(self, model):
        # return (
        #     db.query(model)
        #     .outerjoin(TBL_COUNTRY, TBL_COUNTRY.id == model.country_id)
        #     .outerjoin(TBL_PROVINCE, TBL_PROVINCE.id == model.province_id)
        #     .outerjoin(TBL_DISTRICT, TBL_DISTRICT.id == model.district_id)
        #     .outerjoin(TBL_COMMUNE, TBL_COMMUNE.id == model.commune_id)
        #     .outerjoin(TBL_VILLAGE, TBL_VILLAGE.id == model.village_id)
        # )
        return (
            JoinHelper(db, model)
            # .outerjoin(TBL_COUNTRY, TBL_COUNTRY.id == model.country_id)
            # .outerjoin(TBL_PROVINCE, TBL_PROVINCE.id == model.province_id)
            # .outerjoin(TBL_DISTRICT, TBL_DISTRICT.id == model.district_id)
            # .outerjoin(TBL_COMMUNE, TBL_COMMUNE.id == model.commune_id)
            # .outerjoin(TBL_VILLAGE, TBL_VILLAGE.id == model.village_id)
            .get_query()
        )
        
    def create_integration_data(self): 
        # branch_id = core_lib.get_module_id(db, "Branch", self.current_user.token_working_company_id)
        branch_id = 'HQ'
        ula_id = core_lib.get_module_id(db, "User Location Assignment", self.current_user.token_working_company_id)

        super_user = check_is_superuser(db, self.current_user)

        try:
            audit = {
                "re_created_at"    : datetime.now(),
                "re_created_by"    : self.current_user.id,
                "re_updated_at"    : datetime.now(),
                "re_updated_by"    : self.current_user.id,
                "system_date"       : datetime.now(),
                "authorization": [
                    {
                        "id": self.current_user.id,
                        "status": "APPROVED",
                        "datetime": str(datetime.now())
                    }
                ],
                "branch_id"        : branch_id,
                "company_id"       : self.item.get("id", ""),
            }

            # Branch Creation
            branch_data = {
                "id"                : branch_id,
                "name"              : "HQ",
                "name_lc"           : "ស្នាក់ការកណ្តាល",
                "phone"             : self.item.get("phone", ""),
                "email"             : self.item.get("email", ""),
                "manager_name"      : "Default Manager",
                # "opening_date"      : date.today(),
                "country_id"        : self.item.get("country_id", ""),
                "province_id"       : self.item.get("province_id", ""),
                "district_id"       : self.item.get("district_id", ""),
                "commune_id"        : self.item.get("commune_id", ""),
                "village_id"        : self.item.get("village_id", ""),
                "street_no"         : self.item.get("street_no", ""),
                "house_no"          : self.item.get("house_no", ""),
                "lat_long"          : self.item.get("lat_long", ""),
                "image"             : self.item.get("logo", ""),
                "active"            : True,
                "open_hours"        : "08:00:00",
                "close_hours"       : "17:00:00",
                "account_id"        : None,
                "qr_image"          : None,
                **audit,
            }

            if not super_user: 
                ula_data = {
                    "id"                    : ula_id,
                    "user_id"               : self.current_user.id,
                    "accessible_company_id" : self.item.get("id", ""),
                    "accessible_branch_ids" : branch_id,
                    "default_branch_id"     : branch_id,
                    "role_id"               : 'ADMIN',
                    **audit,
                }

                ula = TBL_USER_LOCATION_ASSIGNMENT(**ula_data)
                db.add(ula)

            branch  = TBL_BRANCH(**branch_data)
            db.add(branch)
            db.commit()
            
        except Exception as e:
            db.rollback()
            return False, str(e)
        finally: 
            return True, ''
        
    def before_save(self):
        return self.create_integration_data()

    def get_header_sub(self):
        return {
            'emp_docu_items': [
                {"field": "id", "text": "ID"},
                {"field": "doc_type", "text": "DOC Type"},
                {"field": "attachment", "text": "Attachment"},
                {
                    "label": "attachment_link",
                    "concat": [
                        {
                            "field": "attachment",
                            "separator": f"{os.getenv('APP_URL', '')}/static/images/Banner/"
                        }
                    ],
                    "text": "Attachment Link"
                },
                {"field": "note", "text": "Note"},
            ]
        }
    
    def get_list_query_obj(self, model):
        return db.query(model).\
			outerjoin(TBL_COMPANY_DOCUMENT, TBL_COMPANY_DOCUMENT.parent_id==model.id)

    def before_delete(self):
        if not self.get_num_of_auth():
            return False, {'id':'Cannot delete company.'}
        
        return True, ''
    

crud = COMPANY_CRUD_API('Company','companies', TBL_COMPANY,{}, schema=CompanySchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Company'])

@app.get('/api/v1/wb/list-current-user-access-companies', tags=['Company'])
def list_current_user_access_companies(
    current_user: Annotated[User, Depends(get_current_active_user)],
    filter      : str = '',
    sort        : str = '',
    search      : str = '',
    page        : int = 1,
    size        : int = 10,
    db          : Session = Depends(get_db),
):  
    try:
        is_superuser = check_is_superuser(db, current_user)
        if is_superuser:
            obj = db.query(TBL_COMPANY.id, TBL_COMPANY.name)

        else:
            obj = db.query(TBL_COMPANY.id,TBL_COMPANY.name).\
            join(TBL_USER_LOCATION_ASSIGNMENT, TBL_USER_LOCATION_ASSIGNMENT.accessible_company_id==TBL_COMPANY.id).\
            filter(TBL_USER_LOCATION_ASSIGNMENT.user_id==current_user.id)
        
        module_name = 'Company'
        field_summary = {
            'sum'  : [],
            'count': []
        }
        header = [
            {"field": "id", "text": "ID"},
            {"field": "name", "text": "Company Name"},
        ]
        model = TBL_COMPANY
        return customFilter(
            obj,
            header,
            model,
            field_summary,
            module_name,
            filter,
            sort,
            search,
            page,
            size
        )

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()


@app.get("/api/v1/wb/get-accessible-company", tags=["Company"])
def get_accessible_company(
    current_user: Annotated[User, Depends(get_current_active_user)],
    page        : int = Query(1, description="Page number"),
    size        : int = Query(10, description="Page size"),
    filter      : str = "",
    sort        : str = "",
    search      : str = "",
    db          : Session = Depends(get_db)
):
    try:
        header = [
            {"field": "id", "text": "ID"},
            {"field": "name", "text": "Company Name"},
        ]
        if check_is_superuser(db, current_user):
            query = db.query(TBL_COMPANY)

        else:
            query = (
                db.query(
                    TBL_COMPANY.id,
                    TBL_COMPANY.name,
                )
                .join(
                    TBL_USER_LOCATION_ASSIGNMENT,
                    TBL_USER_LOCATION_ASSIGNMENT.accessible_company_id
                    == TBL_COMPANY.id,
                )
                .filter(TBL_USER_LOCATION_ASSIGNMENT.user_id == current_user.id)
            )

        return customFilterWithCustomFields(
            obj           = query,
            header        = header,
            model         = TBL_COMPANY,
            field_summary = [],
            module_name   = "Company List",
            filter        = filter,
            sort          = sort,
            search        = search,
            page          = page,
            size          = size
        )

    except Exception as e:
        db.rollback()
        raise e
    
    finally:
        db.close()