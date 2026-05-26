from .models import *
from pydantic import BaseModel, model_validator, root_validator
from typing import Annotated
from fastapi import Path
from enum import Enum
from icb.core.crud_api import *
from icb.core.lib import get_lang as ___

class ModelName(str, Enum):
    UUID              = "UUID"
    Sequencial        = "Sequencial"
    SequencialByDay   = "SequencialByDay"
    SequencialByMonth = "SequencialByMonth"
    SequencialByYear  = "SequencialByYear"
    
class TypeName(str, Enum):
    standard = "standard"
    custom   = "custom"
    label    = "label"

class ListTypeValue(str, Enum):
    LBB   = "LBB"
    LBABS = "LBABS"
    LABS  = "LABS"
class ModuleSchema(BaseModel):
	id              : str | None = None
	name            : str
	num_of_auth     : int | None = 0
	url             : str | None = ''
	model           : str | None = ''
	mask_field      : str | None = ''
	list_view       : ListTypeValue
	query_list      : ListTypeValue
	enable_log      : bool | None = False
	log_action      : str | None = 'ALL'
 
	@model_validator(mode="before")
	def validate_module_name(cls, values: dict):
		name       = values.get('name', None)
		id         = values.get('id', None)
		error_list = {}
		lang       = values.get('lang', 'en')

		if not name:
			error_list.update(dict(name=f"{___('required_data', {}, lang)} name"))
		else:
			module = db.query(TBL_MODULE) \
					.filter(
						TBL_MODULE.name == name,
						TBL_MODULE.id != id
					) \
					.first()

			if module:
				error_list.update(dict(name=f"This module name is already existed."))

		if error_list:
			raise ValueError(error_list)
		else:
			return values
		
class ModuleAccessmentSchema(BaseModel): 
	id              : str | None = None
	name 			: str
	
class ModuleAccessmentItemSchema(BaseModel): 
	id 				: str | None = None
	module_id 		: str
	num_of_record	: int | None = 1

class ModuleAssignmentSchema(BaseModel): 
	id              		: str | None = None
	module_accessment_id    : str
	assigned_company_id     : str

class ModuleAccessmentSubListSchema(BaseModel): 
	module_accessment_items 	: list[ModuleAccessmentItemSchema] | None

class FormModuleSchema(BaseModel):
	id              : str | None = None
	module_id       : str
	num_of_auth     : int | None = 0
	list_view       : ListTypeValue
	query_list      : ListTypeValue


class AutoIDSchema(BaseModel):
	id              : str | None = None
	module_id       : str
	id_type         : Annotated[ModelName, Path(title="ID type: UUID, Sequencial, SequencialByDay, SequencialByMonth, SequencialByYear")] | None = None
	id_prefix       : str | None = ''
	id_index        : Annotated[int, Path(title="Starting ID of module", ge=0)]
	id_date_format  : str | None = '%Y%m%d'
	id_serial_length: int | None = 1
