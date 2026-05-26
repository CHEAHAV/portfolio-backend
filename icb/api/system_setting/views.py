from main import app
from icb.core.crud_api import CRUDAPI
from .models import *
from .schemas import *
import os

class SYSTEM_SETTING_CRUD(CRUDAPI):
    query_fields = ['id']
    addons_fields = []
    
    def get_header(self):
        return [
          {'field':'id', 'text': 'ID'},
          {'field':'token_timeout', 'text': 'Token Timeout'},
          {'field':'login_attempt', 'text': 'Login Attempt'},
          {'field':'otp_limit', 'text': 'OTP Limit'},
          {'field':'system_online', 'text': 'System Online'},
          {'field':'default_password', 'text': 'Default Password'},
          {'field':'pos_source_type', 'text': 'POS Source Type'},
          {'field':'telegram_bot_token', 'text': 'Telegram Bot Token'},
          {'field':'telegram_chat_id', 'text': 'Telegram Chat ID'},
          {'field':'eod_option', 'text': 'EOD Option'},
          {'field':'telegram_sale_bot_token', 'text':'Telegram Sale Bot Token'},
          {'field':'telegram_sale_chat_id', 'text':'Telegram Sale Chat ID'},
          {'field':'saturday', 'text': 'Saturday'},
          {'field':'sunday', 'text': 'Sunday'},
          {'field':'absent_after', 'text': 'Absent After'},
          {'field':'late_after', 'text': 'Late After'},
          {'field':'missed_after', 'text': 'Missed After'},
        ]

crud = SYSTEM_SETTING_CRUD('SystemSetting', 'system-setting',  TBL_SYSTEM_SETTING, {}, schema=SystemSettingSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['System Setting'])
