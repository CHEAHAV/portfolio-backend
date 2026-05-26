from pydantic import BaseModel

class CommuneSchema(BaseModel):
    id         : str | None = None
    name       : str
    name_lc    : str
    district_id: str
    description: str | None = None
    image      : str