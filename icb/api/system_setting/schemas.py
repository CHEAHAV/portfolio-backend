from enum import Enum
from .models import *
from pydantic import BaseModel, Field, model_validator, root_validator
from typing import Dict,Any
from icb.core.db import db
from icb.core.lib import get_lang as ___

class InventoryMethod(Enum):
    WAC  = 'WAC'
    FIFO = 'FIFO'
    LIFO = 'LIFO'
    
class SystemSettingSchema(BaseModel):
    id                    : str        = Field(default='1')
    token_timeout         : int        = 0
    login_attempt         : int        = 5
    otp_limit             : int        = 0
    system_online         : bool       = True
    default_password      : str | None = None
    telegram_bot_token    : str | None = None
    telegram_chat_id      : str | None = None
    
    
    # User can create only one record
    @model_validator(mode="before")
    def validate_fields(cls, values: Dict[str, Any]):
        current_id = values.get('id')
        lang = values.get('lang')
        system_setting = db.query(TBL_SYSTEM_SETTING).first()

        if system_setting and current_id != system_setting.id:
            raise ValueError(___('can_not_create_new_record',{},lang))
        
        return values
