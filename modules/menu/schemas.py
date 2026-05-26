
from pydantic import BaseModel

# The validation for module menu
class MenuSchema(BaseModel):
    id         : str | None = None
    description: str
    ordering   : int
 
    
 
# The validation for module sub menu
class SubMenuSchema(BaseModel):
    id       : str         | None = None
    label    : str
    main_id  : str    | None    = None
    icon     : str       | None = None
    url      : str        | None = None
    type     : str       | None = None
    module_id: str      | None = None
    ordering : int
 
    # @validator('module_id', allow_reuse=True)
    # def validate_module_id(cls, value: str):
    # 	if not value:
    # 		raise ValueError('module ID is required')
    # 	return value


# The sub menu list
class SubMenuListSchema(BaseModel):
    sub_menu: list[SubMenuSchema]  | None = None 

    

class MenuItemSchema(BaseModel):
    id       : str | None = None
    type     : str | None = None
    label    : str
    module_id: str | None = None
    url      : str | None = None
    icon     : str | None = None
