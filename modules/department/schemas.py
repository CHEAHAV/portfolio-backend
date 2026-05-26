from pydantic import BaseModel

class DepartmentSchema(BaseModel):
    id         : str | None = None
    name       : str
    description: str
    image      : str
    active     : bool