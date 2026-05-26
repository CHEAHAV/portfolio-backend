from pydantic import BaseModel

class ProvinceSchema(BaseModel):
    id         : str | None = None
    name       : str
    name_lc    : str
    country_id : str
    description: str | None = None
    image      : str