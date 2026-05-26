from .models import *
from pydantic import BaseModel,Field, model_validator
from datetime import date, time
from decimal import Decimal

class BranchSchema(BaseModel):
	id           : str | None  = Field(default=None, max_length=64, title="ID")
	name         : str | None  = Field(default=None, max_length=100, title="Name")
	name_lc      : str | None  = Field(default=None, max_length=250, title="Name (Local)")
	phone        : str | None  = Field(default=None, max_length=18, title="Phone")
	email        : str | None  = Field(default=None, max_length=40, title="Email")
	manager_name : str | None   = Field(default=None, max_length=64, title="Manager Name")
	opening_date : date | None  = Field(default=None, title="Opening Date")
	country_id   : str | None  = Field(default=None, max_length=64, title="Country ID")
	province_id  : str | None  = Field(default=None, max_length=64, title="Province ID")
	district_id  : str | None  = Field(default=None, max_length=64, title="District ID")
	commune_id   : str | None  = Field(default=None, max_length=64, title="Commune ID")
	village_id   : str | None  = Field(default=None, max_length=64, title="Village ID")
	street_no    : str | None  = Field(default=None, max_length=50, title="Street No")
	house_no     : str | None  = Field(default=None, max_length=50, title="House No")
	lat_long     : str | None  = Field(default=None, max_length=30, title="Latitude/Longitude")
	image        : str | None  = Field(default=None, max_length=60, title="Image")
	active       : bool        = Field(default=True, title="Active")
	open_hours   : time | None = Field(default=None, title="Open Hours")
	close_hours  : time | None = Field(default=None, title="Close Hours")
	account_id   : str | None  = Field(default=None, max_length=64, title="Account ID")
	qr_image     : str | None  = Field(default=None, max_length=60, title="QR Image")
	distance	 : int | None  = Field(default=100)
 
 
	@model_validator(mode="before")
	def validate_values(cls, values: dict):
		if not values.get('opening_date', None):
			values['opening_date'] = None

		if not values.get('open_hours', None):
			values['open_hours'] = None
   
		if not values.get('close_hours', None):
			values['close_hours'] = None
			   
		return values

