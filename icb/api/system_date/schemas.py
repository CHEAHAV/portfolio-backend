from .models import *
from pydantic import BaseModel, model_validator, root_validator
from typing import Dict,Any
from icb.core.db import db
from icb.core.lib import get_lang as ___

class SystemDateSchema(BaseModel):
	id: str | None = None
	current_system_date: str
 
	# User can create only one record
	@model_validator(mode="before")
	def validate_fields(cls, values: Dict[str, Any]):
		current_id = values.get('id')
		lang = values.get('lang')
		system_date = db.query(TBL_SYSTEM_DATE).first()

		if system_date and current_id != system_date.id:
			raise ValueError(___('can_not_create_new_record',{},lang))
		
		return values
