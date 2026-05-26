from pydantic import BaseModel

class FilterSchema(BaseModel):
    id         : str | None = None
    name       : str | None = None
    active     : bool