import re
from datetime import date, datetime
from typing import ClassVar

from fastapi import File, HTTPException, UploadFile
from pydantic import BaseModel, EmailStr, Field, model_validator

from icb.core.db import db
from icb.core.lib import get_lang as ___
from icb.core.security import check_valid_password

# from ..gender.models import *
from .models import *
from enum import Enum

class EmployeeStatus(str, Enum): 
  Active    = 'Active'
  Inactive  = 'Unactive'

# class UserRoleAssignment(BaseModel): 
#   accessible_company_id : str | None = None
#   accessible_branch_ids : str | None = None
#   default_branch_id     : str | None = None
#   role_id               : str | None = None
#   is_default            : bool = False

class UserLocatinAssignmentSchema(BaseModel):
  id                   : str | None = None
  user_id              : str
  accessible_company_id: str
  accessible_branch_ids: str
  default_branch_id    : str
  role_id              : str
  default_store_id     : str
  accessible_stores    : dict
  is_default           : bool = False

class UserSchema(BaseModel):
  id                : str | None = None
  first_name        : str | None = None
  last_name         : str | None = None
  # date_of_birth     : str | None = None
  # gender            : str
  language          : str = Field(default='en', title="Language", max_length=3)
  # base_company_id   : str
  # base_branch_id    : str
  email             : EmailStr
  username          : str
  phone             : str
  password          : str | None = None
  is_active         : bool = False
  require_reset_password: bool = False
  # status            : EmployeeStatus = Field(default=EmployeeStatus.Active, title="Status")
  # employee_id       : str | None = None

  # User Location Assignment
  roles             : list[UserLocatinAssignmentSchema]

  @model_validator(mode="before")
  def check_password(cls, values: dict):
      pwd = values.get('password') 

      # Only validate password if it's provided (not None and not empty string)
      if pwd is not None and pwd.strip():
          if check_valid_password(pwd) != True:
              raise ValueError({'password':'Password is not strong. It must contain number, symbols, lowercase and uppercase letter'})
      
      return values

  # @validator('username', )
  # def validate_username(cls, value: str, values, **kwargs):
  #   print(values, kwargs)
  #   obj = db.query(TBL_USER).filter(TBL_USER.username==value).first()
  #   if obj:
  #       raise ValueError('username is already exist')
  #   else:
  #       return value

  # @model_validator(mode="before")
  # def check_names_differs(cls, values: dict):
  #   firstname = values.get('firstname')
  #   lastname = values.get('lastname')

  #   if firstname is None or lastname is None:
  #       raise ValueError('fields firstname and lastname are not optional')
  #   if firstname == lastname:
  #       raise ValueError('firstname and lastname cannot be the same')
  #   else:
  #       return values

class UserRoleSchema(BaseModel):
  id: str | None = None
  role_id: str
  
  
class UserCashAccountSchema(BaseModel):
  id         : str | None = None
  currency_id: str
  account_id : str
  company_id : str
  branch_id  : str


class UserRoleListSchema(BaseModel):
  # role_list          : list[UserRoleSchema] | None              = None
  account_list       : list[UserCashAccountSchema] | None       = None
  # location_assignment: list[UserLocatinAssignmentSchema] | None = None

          
class CommentUserSchema(BaseModel):
  comment: str

class ExternalUserSchema(BaseModel):
  id: str | None = None
  first_name: str | None = None
  last_name: str | None = None
  date_of_birth: str | None = None
  gender: str
  language: str = Field(default='en', title="Language", max_length=3)
  email: EmailStr
  username: str
  phone: str
  password: str | None = None
  is_active: bool = False
  notification: bool = False
  
class UserChangePasswordSchema(BaseModel):
  old_password: str
  new_password: str
  new_password_confirm: str

class UserResetPINSchema(BaseModel):
  old_pin: str
  new_pin: str
  new_pin_confirm: str

class UserSetPINSchema(BaseModel):
  new_pin: str
  new_pin_confirm: str

class UserDeviceTokenSchema(BaseModel):
  token: str

class UserRegisterSchema(BaseModel):
  username: str
  email: EmailStr
  phone: str
  password: str
  password_confirm: str
  
  @model_validator(mode="after")
  def check_validation(cls, values: dict):
    pwd = values.get('password')
    pwd_confirm = values.get('password_confirm')
    username = values.get('username')
    email = values.get('email')
    id = values.get('id')
    
    username = db.query(TBL_USER).filter(TBL_USER.username==username).first()
    if username and username.id != id:
        raise ValueError('Username is already exist')
      
    user_email = db.query(TBL_USER).filter(TBL_USER.email==email).first()
    if user_email and user_email.id != id:
        raise ValueError('Email is already exist')
    

    if check_valid_password(pwd)!=True:
        raise ValueError('Password is not strong. It must contain number, symbols, lowercase and uppercase letter')

    if pwd != pwd_confirm:
        raise ValueError('Password confirm is not matched')

    return values

class PhoneRegisterSchema(BaseModel):
  phone_number : str

class RegisterConfirmOTPSchema(BaseModel):
  phone_number : str
  otp : str

class RegisterInfoSchema(BaseModel):
  phone_number : str
  full_name : str
  date_of_birth : str
  gender : str


class PhoneLoginSchema(BaseModel):
  phone_number : str

class LoginConfirmOTPSchema(BaseModel):
  phone_number : str
  otp : str


class LoginPasswordSchema(BaseModel):
  username : str
  password : str

class ViewOTPSchema(BaseModel):
  encoded_text : str

class BranchIdSchema(BaseModel):
  branch_id : str

class CompanyIdSchema(BaseModel):
  company_id : str

class UserChangeLanguageSchema(BaseModel):
  lang : str = Field(default='en', title="Language")


''' 
  Item to register user in different type
'''
# ---> Personal Info (Student & Candidate)

class PersonalInfoData(BaseModel):
  full_name: str = Field(..., title="Full Name", max_length=100)
  gender: str = Field(..., title="Gender")
  phone_number: str
  date_of_birth: str | None = None
  province_id: str = Field(..., title="Address")
  confirmed_term: bool | None = False
  education: str | None = None
  occupation: str | None = None

  @model_validator(mode="before")
  def check_personal_validation(cls, values: dict):
    error_list = {}
    lang = values.get('lang')
    # Check validation only with language
    if lang != None:
      full_name = values.get('full_name')
      if not full_name:
        error_list.update(dict(full_name=f"{___('required_data',{},lang)} full name"))

      gender = values.get('gender')
      if not gender:
        error_list.update(dict(gender=f"{___('required_data',{},lang)} gender"))
      
      # gobj = db.query(TBL_GENDER).get(gender)
      # if not gobj:
      #   error_list.update(dict(gender=f"{___('value_not_found',{},lang)} gender"))

      province_id = values.get('province_id')
      if not province_id:
        error_list.update(dict(province_id=f"{___('required_data',{},lang)} province_id"))

      # education = values.get('education')
      # if not education:
      #   error_list.update(dict(education=f"{___('required_data',{},lang)} education"))

      # occupation = values.get('occupation')
      # if not occupation:
      #   error_list.update(dict(occupation=f"{___('required_data',{},lang)} occupation"))

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
  
class ProfileInfoSchemas(BaseModel):
  full_name: str = Field(..., title="Full Name", max_length=100)
  gender: str = Field(..., title="Gender")
  phone_number: str
  date_of_birth: str | None = None
  province_id: str = Field(..., title="Address")
  # education: str = Field(..., title="Education Level")
  # occupation: str = Field(..., title="Occupation")
  education: str | None = None
  occupation: str | None = None

  @model_validator(mode="before")
  def check_personal_validation(cls, values: dict):
    error_list = {}
    lang = values.get('lang')
    # Check validation only with language
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

      # education = values.get('education')
      # if not education:
      #   error_list.update(dict(education=f"{___('required_data',{},lang)} education"))

      # occupation = values.get('occupation')
      # if not occupation:
      #   error_list.update(dict(occupation=f"{___('required_data',{},lang)} occupation"))

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
  
class KCUserUpdateSchema(BaseModel):
    id            : str | None = None
    first_name    : str | None = None
    last_name     : str | None = None
    date_of_birth : str | None = None
    gender        : str | None = None
    language      : str        = "en"
    phone         : str | None = None
    password      : str | None = None
    require_reset_password: bool = False
    is_active     : bool       = True
    status        : str        = "Active"
    roles         : list[UserLocatinAssignmentSchema]  # ✅ reused


class KCUserRegisterSchema(BaseModel):
    first_name      : str
    last_name       : str
    username        : str
    email           : str
    phone           : str
    password        : str
    confirm_password: str


class KCForgotPasswordLinkRequest(BaseModel):
    username: str
    email   : str


class KCForgotPasswordOTPRequest(BaseModel):
    username: str
    email   : str


class KCVerifyResetCodeRequest(BaseModel):
    username: str
    code    : str


class KCConfirmResetPasswordRequest(BaseModel):
    username    : str
    code        : str
    new_password: str


class KCResetPasswordRequest(BaseModel):
    new_password: str
    temporary   : bool = False
