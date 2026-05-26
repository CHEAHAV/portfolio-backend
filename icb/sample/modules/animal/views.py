
import json
from sqlalchemy import func, cast, String
from modules.branch.models import TBL_BRANCH
from modules.gender.models import TBL_GENDER
from modules.animal.models import *
from modules.animal.schemas import AnimalSchema, AnimalSubListSchema
from modules.color.models import TBL_COLOR
from core.crud_api import CRUDAPI
from main import app
from sqlalchemy import select, func, cast
from sqlalchemy.dialects.postgresql import ARRAY, INTEGER, JSON

class ANIMAL_CRUD_API(CRUDAPI):
    query_fields = ['name']
    query_list_fields = ['name']
    query_fields_2  = ['gender_id']
    query_fields_3  = ['description']

    def get_header(self):
        return [
            {"field": "id", "text": "ID"},
            {"field": "name", "text": "Module Name"},
            {"field": "number_of_leg", "text": "Number of Leg"},
            {"field": "number_of_hand", "text": "Number of Hand"},
            {"field": "gender_id", "text": "Gender ID"},
            {"field": "description", "model": TBL_GENDER, "label":"gender_name", "text": "Gender Name"},
            {"field": "color_id", "text": "Color ID"},
            {"label": "color_obj", "func": (
                select(
                    func.coalesce(
                        func.json_agg(
                            func.json_build_object(
                                "id", TBL_COLOR.id,
                                "name", TBL_COLOR.name
                            )
                        ),
                        func.cast("[]", JSON)
                    )
                )
                .select_from(TBL_COLOR)
                .where(
                    TBL_COLOR.id.in_(
                        select([
                            func.unnest(
                                func.string_to_array(self.model.color_id, ",")
                            )]
                        )
                    )
                )
                .correlate(self.model)
                .scalar_subquery()
            ), "text": "Color Object"},#sample of json_agg with correlated subquery id data format: RED,BLUE
            {"field": "name", "model": TBL_COLOR, "label":"color_name", "text": "Color Name"},
            {"field": "", "concat": [
                {'field': 'number_of_leg', 'separator': 'This animal has'}, 
                {'field': 'number_of_hand', 'separator': ' legs and '},
                {'field': 'name', 'model': TBL_COLOR, 'separator': ' hands with color '}
            ], "label":"legs_and_hands", "text": "Legs - Hands"},
            {"case": [
                # {'field':'field_name','op':'custom','when': TBL_COLOR.id=='RED', 'then': 'I am red color'},
                {'when': TBL_COLOR.id=='RED', 'then': 'I am red color'},
                {'when': TBL_COLOR.id=='BLUE', 'then': TBL_COLOR.name},
                {'when': TBL_COLOR.id=='BLUE1', 'then': 'I am red blue'},
                {'when': TBL_COLOR.id=='GREEN', 'then': [[TBL_COLOR,'id'], [TBL_COLOR,'name'], 'is green color']}
            ], "else":"else case", "label":"leg_type", "text": "Leg Type"},
            {"field": "description", "text": "Description"},
            # {"json_agg": [
            #     {'field': 'id', 'model': TBL_ANIMAL_CHILD},
            #     {'field': 'name', 'model': TBL_ANIMAL_CHILD},
            # ], "label": "children", "text": "Children"},
            # {"func": func.string_agg(func.concat(
            #     TBL_ANIMAL_CHILD.id, TBL_ANIMAL_CHILD.name), ', '), 
            # "label": "child_name", "text": "Children"},
            {"func": (
                select(
                    func.string_agg(TBL_ANIMAL_CHILD.name, ",")
                )
                .select_from(TBL_ANIMAL_CHILD)
                .where(TBL_ANIMAL_CHILD.parent_id == self.model.id)   # 👈 correlated here
                .correlate(self.model)
                .scalar_subquery()
            ), "label":"my_child_name", "text":"Branch Name"}
        ]
    '''
    {
        "id":"id_value",
        "name":"name_value",
        "children": [
            {
                "id":"id_value",
                "name":"name_value1"
            },
            {
                "id":"id_value",
                "name":"name_value2"
            }
        ],
        "child_name": "id_valuename_value1, id_valuename_value2"
    }
    '''     
    def get_list_query(self, model):
        return self.db.query(model).\
            outerjoin(TBL_COLOR, TBL_COLOR.id == model.color_id).\
            outerjoin(TBL_GENDER, TBL_GENDER.id == model.gender_id).\
            outerjoin(TBL_ANIMAL_CHILD, TBL_ANIMAL_CHILD.parent_id == model.id)
            # group_by(
            #     model.id,
            #     model.name, 
            #     model.number_of_leg, 
            #     model.number_of_hand, 
            #     model.color_id, 
            #     model.gender_id, 
            #     model.description, 
            #     model.re_is_public,
            #     model.re_created_at,
            #     model.re_created_by,
            #     model.re_version,
            #     model.flow_status,
            #     model.re_updated_at, 
            #     model.re_updated_by,
            #     model.re_status,
            #     model.branch_id,
            #     model.authorization,
            #     TBL_COLOR.id, 
            #     TBL_COLOR.name, 
            #     TBL_GENDER.id,
            #     TBL_GENDER.description
            # )
        
    
    def get_header_sub(self):
        return {
            "child": [
                {"field": "id", "text": "ID"},
                {"field": "name", "text": "Child Name"},
                {"field": "gender_id", "text": "Gender ID"},
                {"field": "description", "model": TBL_GENDER, "label":"gender_name", "text": "Gender Name"},
            ]
        }
    
    def get_vsi_query(self, record_type=''):
        model = getattr(self.moduleList, str(self.sub_models.get('child').__name__) + record_type)
        obj   = self.db.query(model).outerjoin(TBL_GENDER, TBL_GENDER.id == model.gender_id)
        return { 'child': obj }
    
    def before_save(self):
        self.current_user
        # get main item data
        item = self.item
        # modify field value before save
        if not item.get('number_of_leg'):
            self.item['number_of_leg'] = 4

        # remove field before save
        self.item.pop('description', None)
        # validation before save with return False to stop saving
        if self.item.get('number_of_hand')<0:
            return False, {"number_of_hand":"Number of hand cannot be negative"}
        
        # validation with raise exception
        '''
        {
            "field_name1": "error message1",
            "field_name2": "error message2"
            "child": {
                "0": {
                    "name": "Child name is required"
                },
                "2": {
                    "name": "Child name is required"
                }
            }
        }
        '''
        sub_item_children = self.sub_item.get('child', [])
        errors = {}
        count = 0
        for child in sub_item_children:
            error = {}
            if not child.get('name'):
                error['name'] = "Child name is required"
            if error:
                errors[str(count)] = error
            count += 1

        if errors:
            full_errors = {'child': errors}
            raise ValueError(full_errors)

        return True, ""
    
    def before_approve(self):
        self.current_user
        self.id
        return True, ""
    
    def after_approve(self):
        return True, ""
    def after_save(self):
        return True, ""
    def after_delete(self):
        return True, ""
    def after_update(self):
        return True, ""
    def before_delete(self):
        return True, ""
    def before_update(self):
        return True, ""
    def before_revert(self):
        return True, ""
    def after_revert(self):
        return True, ""
    def before_reject(self):
        return True, ""
    def after_reject(self):
        return True, ""
    
    def before_response(self, data, obj=None):
        ''''
            data: list of dictionary
            obj: SQLAlchemy object
        '''
        return data
    
    def after_listed(self):
        pass

    def update_request_filters(self, filters):
        '''
            filters:string
            sample data: [{"field":"name","value":"an","operation":"=="},{"field":"name","value":"an","operation":"like"}]
            return: string
        '''
        filters = json.loads(filters) if filters else []
        # filters.append({"field":"number_of_leg", "operation":">", "value":2})
        # filters.append({"field":"color_id", "operation":"==", "value":"GREEN"})
        filters = json.dumps(filters)
        return filters
    
    def after_viewed(self):
        pass

    def before_view_response(self, item):
        ''''
            item: dictionary
        '''
        item['item']['info'] = "This is additional info added in before_view_response"
        item['info'] = "This is additional info added in before_view_response"
        return item

crud = ANIMAL_CRUD_API('Animal', 'animals', TBL_ANIMAL, 
                       {'child':TBL_ANIMAL_CHILD}, 
                       schema=AnimalSchema,
                       sub_schema= AnimalSubListSchema,
                       schema_edit=AnimalSchema,
                       sub_schema_edit= AnimalSubListSchema
                      )
crud.init_route(disable_route=['template','delete'])
app.include_router(crud.router, prefix="/api/v1", tags=['Animal'])

'''

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



'''
