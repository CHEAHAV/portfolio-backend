from main import app, Body
from icb.core.crud_api import *
from .models import *
from .schemas import *


class CUSTOM_CRUDAPI(CRUDAPI):
    query_fields = ['current_system_date']

    def get_header(self):
        return [
                {"field": "id", "text": "ID"},
                {"field": "current_system_date", "text": "Current System Date"}
            ]


crud = CUSTOM_CRUDAPI('SystemDate','system-date', TBL_SYSTEM_DATE,{},schema=SystemDateSchema)
crud.init_route(['get_comment','list_rejected'])
app.include_router(crud.router, prefix="/api/v1", tags=['System Date'])


@app.get("/api/v1/wb/get-current-system-date", tags=['System Date'])
def get_current_system_date( current_user: Annotated[User, Depends(get_current_active_user)] ):
    try:
      
      obj = db.query(TBL_SYSTEM_DATE).first()
      
      return obj.current_system_date if obj else ''
      
    except Exception as e:
        return str(e)
      
    finally:
        db.close()