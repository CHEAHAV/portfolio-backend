from pydantic import BaseModel

class InfoSchema(BaseModel):
    id         : str | None = None
    name       : str | None = None
    description: str | None = None
    image      : str | None = None
    active     : bool