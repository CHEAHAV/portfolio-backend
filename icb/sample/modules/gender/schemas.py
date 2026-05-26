
from pydantic import BaseModel, validator,root_validator, Field


class GenderSchema(BaseModel):
    id: str | None = None
    description: str = Field(default=None, title="Description", min_length=1, max_length=10)
    description_lc: str = Field(default=None, title="Description LC", min_length=1, max_length=10)
    