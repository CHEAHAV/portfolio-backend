from typing import Optional, Any
import json
from main import app
from icb.core.crud_api import *
from icb.api.sync_setting.models import *
from icb.api.sync_setting.schemas import *

class CUSTOM_CRUDAPI(CRUDAPI):
    query_fields = ['module_name']
    list_all = True

    def get_header(self):
        return [
            {"field": "id", "text": "ID"},
            {"field": "module_name", "text": "Module Name"},
            {"field": "model_name", "text": "Model Name"},
            {"field": "enable_sync", "text": "Enable Sync"},
            {"field": "sub_model_sync_include", "text": "Sub Model Sync Include"},
        ]

    def get_header_sub(self):
        return {
            'sub_item': [
                {'field': 'id', 'text': 'ID'},
                {'field': 'condition_type', 'text': 'Condition Type'},
                {'field': 'condition', 'text': 'Condition'},
                {'field': 'operator', 'text': 'Operator'},
                {'field': 'value', 'text': 'Value'},
                {'field': 'logic', 'text': 'Logic'},
                {'field': 'group_id', 'text': 'Group ID'},
                {'field': 'args', 'text': 'Args Function'}
            ]
        }

    def before_save(self):
        # Process SyncSettingsSchema data
        data = self.item.copy()  # Work with a copy to avoid modifying during validation
        try:
            if data.get('sub_model_sync_include'):
                self.item['sub_model_sync_include'] = [item.upper().strip() for item in data['sub_model_sync_include'].split(',') if item.strip()]
            else:
                self.item['sub_model_sync_include'] = []

            # Process sub_item (SyncConditionSchema) if present
            for i, cond in enumerate(self.sub_item['sub_item']):
                cond_data = cond.copy()
                if cond_data.get('args'):
                    try:
                        cond_data['args'] = json.loads(cond_data['args'].replace("'", '"'))
                    except json.JSONDecodeError:
                        return False, f"args must be a valid JSON string for condition {cond_data.get('condition')}"
                if cond_data.get('value') and cond_data['operator'] == 'in':
                    cond_data['value'] = [item.strip() for item in cond_data['value'].split(',') if item.strip()]
                # Update the specific sub_item entry
                self.sub_item['sub_item'][i].update(cond_data)

            return True, ""
        except ValueError as e:
            return False, f"Validation error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"

crud = CUSTOM_CRUDAPI('SyncSetting', 'sync-setting', TBL_SYNC_SETTING, {'sub_item': TBL_SYNC_CONDITION}, schema=SyncSettingsSchema, sub_schema=SubSyncConditionSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Sync Setting'])