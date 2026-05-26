from .models import *
from pydantic import BaseModel,EmailStr, HttpUrl, constr, model_validator, root_validator, validator, Field
from typing import ClassVar
from datetime import datetime
from icb.core.lib import get_lang as ___
from enum import Enum

class DocumentType(str, Enum): 
  Leave       = 'Leave'
  Overtime    = 'Overtime'
  Mission     = 'Mission'
  
class CompanySchema(BaseModel):
  id                 : str | None = None
  name               : str =Field(title="Company Name", max_length=100)
  name_lc            : str =Field(title="Company Name (Local)", max_length=100)
  description        : str | None = None
  description_lc     : str | None = None
  logo               : str | None = None
  banner             : str | None = None
  phone              : str
  phone_2            : str | None = None
  telegram           : str | None = Field(max_length=25)
  email              : str | None = Field(max_length=100)
  website            : str | None = Field(max_length=60)
  facebook           : str | None = Field(max_length=100)
  youtube            : str | None = Field(max_length=100)
  country_id         : str
  province_id        : str
  district_id        : str
  commune_id         : str
  village_id         : str
  street_no          : str | None = None
  house_no           : str | None = None
  lat_long           : str | None  = None
  registration_number: str | None = Field(max_length=25)
  vat_tin            : str | None = Field(max_length=25)
  parent_company_id  : str | None = None
  is_group_holding   : bool = False

  @validator('name', 'province_id')
  def validate_required(cls, value: str):
    if not value:
        raise ValueError('This field is required.')
    else:
        return value

class CompanyHRSchema(BaseModel):
  name: str
  phone: str
  email: str
  position: str


class CompanyHRListSchema(BaseModel):
  sub_item: list[CompanyHRSchema]  | None = None 


class Lang:
    __name__='Lang'

lang_singleton = Lang()
class CompanyInfo(BaseModel):
  name: str = Field(..., title="Name")
  commune_id: str = Field(..., title="Commune")
  district_id: str = Field(..., title="District")
  province_id: str = Field(..., title="Province")
  lang: ClassVar[Lang] = lang_singleton
  
  @model_validator(mode="before")
  def check_company_validation(cls, values: dict):
    error_list = {}
    lang = values.get('lang')
    if lang != None:
      name = values.get('name')
      if not name:
        error_list.update(dict(name=f"{___('required_data',{},lang)} name"))
        
      commune_id = values.get('commune_id')
      if not commune_id:
        error_list.update(dict(commune_id=f"{___('required_data',{},lang)} commune_id"))
        
      district_id = values.get('district_id')
      if not district_id:
        error_list.update(dict(district_id=f"{___('required_data',{},lang)} district_id"))

      province_id = values.get('province_id')
      if not province_id:
        error_list.update(dict(province_id=f"{___('required_data',{},lang)} province_id"))

    # raise if any error
    if error_list:
      raise NameError(error_list)

    return values
  
class CompanyDocSchema(BaseModel):
  id        : str | None = None
  doc_type  : DocumentType = Field(default=DocumentType.Leave)
  doc_name  : str | None = None
  attachment: str | None = None
  note      : str | None = None

class RepresentativeInfo(BaseModel):
  full_name: str = Field(..., title="Full Name", max_length=100)
  gender: str = Field(..., title="Gender")
  date_of_birth: str | None = None
  province_id: str = Field(..., title="province_id")

  @model_validator(mode="before")
  def check_personal_validation(cls, values: dict):
    error_list = {}
    lang = values.get('lang')
    if lang != None:
      full_name = values.get('full_name')
      if not full_name:
        error_list.update(dict(full_name=f"{___('required_data',{},lang)} full name"))

      gender = values.get('gender')
      if not gender:
        error_list.update(dict(gender=f"{___('required_data',{},lang)} gender"))

      province_id = values.get('province_id')
      if not province_id:
        error_list.update(dict(province_id=f"{___('required_data',{},lang)} province_id"))

      date_of_birth = values.get('date_of_birth')
      if date_of_birth:
        if len(str(date_of_birth)) == 10:
          try:
            datetime.strptime(str(date_of_birth), "%Y-%m-%d")
          except Exception as e:
            error_list.update(dict(date_of_birth=f"{___('invalid_date',{},lang)}"))
        else:
          error_list.update(dict(date_of_birth=f"{___('invalid_date',{},lang)}"))
      else:
        error_list.update(dict(date_of_birth=f"{___('required_data',{},lang)} date of birth"))

    # raise if any error
    if error_list:
      raise NameError(error_list)

    return values
  
class CompanyContactInfo(BaseModel):
  phone1: constr(max_length=13, min_length=10) = Field(..., title="Phone Number1")
  phone2: constr(max_length=13, min_length=10) = Field(..., title="Phone Number2")
  email: EmailStr = Field(..., title="Email")
  telegram: HttpUrl = Field(..., title="Telegram")
  website: HttpUrl = Field(..., title="Website")
  street_no: str = Field(..., title="Street Number")
  house_no: str = Field(..., title="House Number")
  village_id: str = Field(..., title="Village")
  commune_id: str = Field(..., title="Commune")
  district_id: str = Field(..., title="District")
  province_id: str = Field(..., title="Province")
  lang: ClassVar[Lang] = lang_singleton