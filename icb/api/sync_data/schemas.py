from pydantic import BaseModel, validator
from typing import Any

# Define a Pydantic model for filter validation
class FilterCondition(BaseModel):
    field: str
    operator: str
    value: Any