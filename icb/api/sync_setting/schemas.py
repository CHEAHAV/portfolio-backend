from pydantic import BaseModel
from typing import Optional, List, Any, Dict, Callable

class SyncSettingsSchema(BaseModel):
    module_name: str
    model_name: str
    enable_sync: bool = False
    sub_model_sync_include: str

class SyncConditionSchema(BaseModel):
    condition_type: str  # 'model' or 'function'
    condition: str  # Field name for 'model', function name for 'function'
    operator: str
    value: Any
    logic: Optional[str] = 'AND'
    group_id: Optional[int] = None
    args: str = None

    class Config:
        validate_assignment = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.condition_type not in ['model', 'function']:
            raise ValueError("condition_type must be 'model' or 'function'")
        if self.condition_type == 'model' and not self.condition:
            raise ValueError("For 'model' type, condition (field) is required")
        if self.condition_type == 'function' and not self.condition:
            raise ValueError("For 'function' type, condition (function) is required")
        if self.operator not in ['==', '!=', 'in', '>', '<', '>=', '<=']:
            raise ValueError("Invalid operator")
        if self.logic and self.logic not in ['AND', 'OR']:
            raise ValueError("logic must be 'AND' or 'OR'")

class SubSyncConditionSchema(BaseModel):
    sub_item: list[SyncConditionSchema] | None = None

class SyncCondition:
    def __init__(self, condition_type: str, condition: str, operator: str, value: Any, logic: str = 'AND', group_id: Optional[int] = None, args: Dict[str, Any] = None):
        self.condition_type = condition_type
        self.condition = condition
        self.operator = operator
        self.value = value
        self.logic = logic
        self.group_id = group_id
        self.args = args or {}

    def to_sqlalchemy_filter(self, model):
        if self.condition_type != 'model':
            raise ValueError("to_sqlalchemy_filter is only valid for 'model' type")
        column = getattr(model, self.condition)
        if self.operator == '==':
            return column == self.value
        elif self.operator == '!=':
            return column != self.value
        elif self.operator == 'in':
            return column.in_(self.value)
        elif self.operator == '>':
            return column > self.value
        elif self.operator == '<':
            return column < self.value
        elif self.operator == '>=':
            return column >= self.value
        elif self.operator == '<=':
            return column <= self.value
        else:
            raise ValueError(f"Unsupported operator: {self.operator}")

    def evaluate(self, record):
        if self.condition_type == 'function':
            if self.condition not in custom_functions:
                raise ValueError(f"Function {self.condition} not registered")
            func = custom_functions[self.condition]
            result = func(record, **self.args)
            if self.operator == '==':
                return result == self.value
            elif self.operator == '!=':
                return result != self.value
            elif self.operator == 'in':
                return result in self.value
            elif self.operator == '>':
                return result > self.value
            elif self.operator == '<':
                return result < self.value
            elif self.operator == '>=':
                return result >= self.value
            elif self.operator == '<=':
                return result <= self.value
            else:
                raise ValueError(f"Unsupported operator: {self.operator}")
        return False  # Default for non-function types


# Function registry
custom_functions: Dict[str, Callable] = {}

def register_sync_function(name: str, func: Callable):
    """Register a custom sync function globally."""
    custom_functions[name] = func