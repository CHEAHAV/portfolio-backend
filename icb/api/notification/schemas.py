from typing import List

from .models import *
from pydantic import BaseModel,EmailStr, root_validator, validator



class NotificationSchema(BaseModel):
	id: str | None = None
	module_id: str
	data: str

class NotificationMarkReadSchema(BaseModel):
	notification_ids: List[str]
