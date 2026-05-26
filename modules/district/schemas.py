from pydantic import BaseModel

class DistrictSchema(BaseModel):
    id         : str | None = None
    name       : str
    name_lc    : str
    province_id: str
    description: str | None = None
    image      : str