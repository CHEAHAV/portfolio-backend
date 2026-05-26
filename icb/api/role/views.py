from fastapi import Query

from icb.core.lib import check_is_superuser
from icb.lib.utils import customFilterWithCustomFields
from main import app, Body
from icb.core.crud_api import *
from .models import *
from .schemas import *
from ..user.models import TBL_USER_LOCATION_ASSIGNMENT
from icb.lib.render_api import ResponseModel
from ..branch.models import TBL_BRANCH
from ..company.models import TBL_COMPANY
from sqlalchemy import and_, or_
class CUSTOM_CRUDAPI(CRUDAPI):
    query_fields = ['name']
    def get_header(self):
        return [
            {"field": "id", "text": "ID", "width": "20%", "align": "center", "sortable": True, "searchable": True},
            {"field": "name", "text": "Name", "width": "30%", "align": "left", "sortable": False, "searchable": True},
            {"field": "name_lc", "text": "Name (Local)"},
            {"field": "description", "text": "Description"},
            {"field": "is_superuser", "text": "Super User"},
        ]

crud = CUSTOM_CRUDAPI('Role','roles', TBL_ROLE,{'sub_item':TBL_ROLE_MODULE}, schema=RoleSchema, sub_schema=RoleModuleListSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Role'])

@app.get('/api/v1/get-user-location-assignment', tags=['User'])
def get_user_location_assignment(
    current_user    : Annotated[User, Depends(get_current_active_user)], 
    user_id         : str = Query(default=None),
    db              : Session = Depends(get_db),
):
    try: 
        if not user_id: 
            raise HTTPException(status_code=400, detail="User ID is required")

        query = db.query(TBL_USER_LOCATION_ASSIGNMENT).\
            outerjoin(TBL_BRANCH, 
                and_(
                    TBL_USER_LOCATION_ASSIGNMENT.default_branch_id == TBL_BRANCH.id,
                    TBL_USER_LOCATION_ASSIGNMENT.branch_id == TBL_BRANCH.branch_id, 
                    TBL_USER_LOCATION_ASSIGNMENT.company_id == TBL_BRANCH.company_id,
                )
            ).\
            outerjoin(TBL_COMPANY, and_(
                TBL_USER_LOCATION_ASSIGNMENT.accessible_company_id == TBL_COMPANY.id,
                TBL_USER_LOCATION_ASSIGNMENT.company_id == TBL_COMPANY.company_id,
            )).\
        filter(
            TBL_USER_LOCATION_ASSIGNMENT.user_id == user_id, 
            TBL_USER_LOCATION_ASSIGNMENT.branch_id == current_user.token_working_branch_id, 
            TBL_USER_LOCATION_ASSIGNMENT.company_id == current_user.token_working_company_id,
        ).first()

        if query: 
            return ResponseModel(
                status=200,
                ok=True,
                title='GetUserLocationAssignment',
                message='Get User Location Assignment Successfully',
                module='GetUserLocationAssignment',
                data=query
            )
        
        else: 
            return ResponseModel(
                status=200,
                ok=True,
                title='GetUserLocationAssignment',
                message='Get User Location Assignment Successfully',
                module='GetUserLocationAssignment',
                data=None
            )
        
    except Exception as e: 
        raise e
    finally: 
        db.close()

@app.get('/api/v1/get-company-roles', tags=['Role'])
def get_company_roles(
    current_user    : Annotated[User, Depends(get_current_active_user)], 
    db              : Session = Depends(get_db),
):
    try: 
        query = db.query(TBL_ROLE).filter(
            TBL_ROLE.company_id == current_user.token_working_company_id,
        ).all()

        if query: 
            return ResponseModel(
                status=200,
                ok=True,
                title='GetCompanyRoles',
                message='Get Company Roles Successfully',
                module='GetCompanyRoles',
                data=query
            )
        
        else: 
            return ResponseModel(
                status=200,
                ok=True,
                title='GetCompanyRoles',
                message='Get Company Roles Successfully',
                module='GetCompanyRoles',
                data=None
            )
        
    except Exception as e: 
        raise e
    finally: 
        db.close()



@app.get("/api/v1/wb/get-role-by-company", tags=["Role"])
def get_role_by_company(
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
            
        query = db.query(TBL_ROLE).filter(
                or_(
                    TBL_ROLE.company_id == company_id,
                    and_(TBL_ROLE.company_id == 'SYSTEM',TBL_ROLE.re_is_public==True))
                )

        return customFilterWithCustomFields(
            obj           = query,
            header        = header,
            model         = TBL_ROLE,
            field_summary = [],
            module_name   = "Role List",
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