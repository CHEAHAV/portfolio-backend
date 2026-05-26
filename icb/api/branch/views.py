import os
from ..store.models import TBL_STORE
from ..user.models import TBL_USER_LOCATION_ASSIGNMENT
from icb.core.lib import check_is_superuser
from icb.lib.utils import customFilterWithCustomFields
from main import app, Body
from icb.core.crud_api import CRUDAPI, get_db, Session, User, Annotated, get_current_active_user
from .models import *
from .schemas import BranchSchema
from fastapi import Depends, HTTPException, Body, status, Path, Query, File, Form, UploadFile, Request


class BRANCH_CRUDAPI(CRUDAPI):
    query_fields = ["name"]
    list_all = True
    
    def get_header(self):
        return [
            {"field" : "id", "text" : "ID"},
            {"field" : "name", "text" : "Name"},
            {"field" : "name_lc", "text" : "Name (Local)"},
            {"field" : "phone", "text" : "Phone"},
            {"field" : "email", "text" : "Email"},
            {"field" : "manager_name", "text" : "Manager Name"},
            {"field" : "opening_date", "text" : "Opening Date"},
            # {"field" : "country_id", "text" : "Country"},
            # {"field" : "name", "model" : TBL_COUNTRY, "label" : "country_name","text":"Country Name"},
            # {"field" : "province_id", "text" : "Province"},
            # {"field" : "name", "model" : TBL_PROVINCE, "label" : "province_name","text":"Province Name"},
            # {"field" : "district_id", "text" : "District"},
            # {"field" : "name", "model" : TBL_DISTRICT, "label" : "district_name","text":"District Name"},
            # {"field" : "commune_id", "text" : "Commune"},
            # {"field" : "name", "model" : TBL_COMMUNE, "label" : "commune_name","text":"Commune Name"},
            # {"field" : "village_id", "text" : "Village"},
            # {"field" : "name", "model" : TBL_VILLAGE, "label" : "village_name","text":"Village Name"},
            {"field" : "street_no", "text" : "Street NO"},
            {"field" : "house_no", "text" : "House NO"},
            {"field": "lat_long", "text": "Latitude/Longitude"},
            {"field" : "image", "text" : "Image"},
            {"label" : "image_link", "concat": [{'field': 'image', 'separator': f"{os.getenv('APP_URL','')}/static/images/Branch/" }], "text": "Image Link"},
            {"field" : "active", "text" : "Active"},
            {"field" : "open_hours", "text" : "Open Hours"},
            {"field" : "close_hours", "text" : "Close Hours"},
            {"field" : "account_id", "text" : "Account ID"},
            {"field" : "qr_image", "text" : "QR Image"},
            {"label" : "qr_image_link", "concat": [{'field': 'qr_image', 'separator': f"{os.getenv('APP_URL','')}/static/images/Branch/" }], "text": "QR Image Link"}, 
            {"field": "distance", "text": "Distance"}
        ]
        
    # def get_list_query(self, model):
    #     return db.query(model).\
    #         outerjoin(TBL_PROVINCE, TBL_PROVINCE.id == model.province_id).\
    #         outerjoin(TBL_DISTRICT, TBL_DISTRICT.id == model.district_id).\
    #         outerjoin(TBL_COMMUNE, TBL_COMMUNE.id == model.commune_id).\
    #         outerjoin(TBL_VILLAGE, TBL_VILLAGE.id == model.village_id).\
    #         outerjoin(TBL_COUNTRY, TBL_COUNTRY.id == model.country_id)
        
    def before_save(self):
        
        return True,''
            
    def after_approve(self):
        return True,''
    
    def after_update(self):
  
            
        return True,''

    def before_delete(self):
        if self.id == 'HQ':
            return False, {'id':'Record cannot be deleted.'}
        
        return True, ''
    
      
crud = BRANCH_CRUDAPI('Branch','branches', TBL_BRANCH,{},schema=BranchSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Branch'])

@app.get("/api/v1/wb/get-access-branch-by-company", tags=["Branch"])
def get_access_branch_by_company(
    current_user: Annotated[User, Depends(get_current_active_user)],
    page        : int = Query(1, description="Page number"),
    size        : int = Query(10, description="Page size"),
    filter      : str = "",
    sort        : str = "",
    search      : str = "",
    company_id  : str = Query(None, description="Company ID"),
    db          : Session = Depends(get_db)
):
    try:
        if not company_id:
            raise HTTPException(status_code=400, detail="Company ID is required")
        
        header = [
            {"field": "id", "text": "ID"},
            {"field": "name", "text": "Name"},
        ]
        access_branch = []

        if not check_is_superuser(db, current_user):
            obj = db.query(
                    TBL_COMPANY.id,
                    TBL_COMPANY.name,
                ).join(
                    TBL_USER_LOCATION_ASSIGNMENT,
                    TBL_USER_LOCATION_ASSIGNMENT.accessible_company_id == TBL_COMPANY.id
                ).filter(
                    TBL_USER_LOCATION_ASSIGNMENT.user_id == current_user.id,
                    TBL_COMPANY.id == company_id
                ).first()
            
            if not obj:
                raise HTTPException(status_code=403, detail="You do not have access to this company")
            
            access_branch = obj.accessible_branch_ids.split(',')
        
        query = db.query(TBL_BRANCH).filter(TBL_BRANCH.company_id == company_id)
        if access_branch:
            query = query.filter(TBL_BRANCH.id.in_(access_branch))

        return customFilterWithCustomFields(
            obj           = query,
            header        = header,
            model         = TBL_BRANCH,
            field_summary = [],
            module_name   = "Branch List",
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