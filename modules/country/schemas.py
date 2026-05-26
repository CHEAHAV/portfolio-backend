from pydantic import BaseModel

class CountrySchema(BaseModel):
    id         : str | None = None
    name       : str
    name_lc    : str
    description: str | None = None
    image      : str