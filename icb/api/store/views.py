
# from ..commune.models import TBL_COMMUNE
# from ..country.models import TBL_COUNTRY
# from ..district.models import TBL_DISTRICT
# from ..province.models import TBL_PROVINCE
# from ..village.models import TBL_VILLAGE
from ..company.models import TBL_COMPANY
from ..store.models import TBL_STORE
from ..user.models import TBL_USER_LOCATION_ASSIGNMENT
from icb.core.lib import check_is_superuser
from icb.lib.utils import customFilterWithCustomFields
from main import app, Body
from icb.core.crud_api import *
from .models import *
from .schemas import StoreSchema


class STORE_CRUD_API(CRUDAPI):
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
            {"field" : "lat_long", "text": "Latitude/Longitude"},
            {"field" : "image", "text" : "Image"},
            {"label" : "image_link", "concat": [{'field': 'image', 'separator': f"{os.getenv('APP_URL','')}/static/images/Branch/" }], "text": "Image Link"},
            {"field" : "active", "text" : "Active"},
            {"field" : "open_hours", "text" : "Open Hours"},
            {"field" : "close_hours", "text" : "Close Hours"},
            {"field" : "qr_image", "text" : "QR Image"},
            {"label" : "qr_image_link", "concat": [{'field': 'qr_image', 'separator': f"{os.getenv('APP_URL','')}/static/images/Branch/" }], "text": "QR Image Link"}, 
            {"field" : "distance", "text": "Distance"}
        ]
        
    # def get_list_query(self, model):
    #     return db.query(model).\
    #         outerjoin(TBL_PROVINCE, TBL_PROVINCE.id == model.province_id).\
    #         outerjoin(TBL_DISTRICT, TBL_DISTRICT.id == model.district_id).\
    #         outerjoin(TBL_COMMUNE, TBL_COMMUNE.id == model.commune_id).\
    #         outerjoin(TBL_VILLAGE, TBL_VILLAGE.id == model.village_id).\
    #         outerjoin(TBL_COUNTRY, TBL_COUNTRY.id == model.country_id)
     
    def after_approve(self):
        self.update_info()
        return True,''
    
    def after_update(self):
        # if not self.get_num_of_auth():
        #     self.update_info()
            
        return True,''

    def before_delete(self):
        if self.id == 'HQ':
            return False, {'id':'Record cannot be deleted.'}
        
        return True, ''
    

crud = STORE_CRUD_API('Store','stores', TBL_STORE,{},schema=StoreSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Store'])
