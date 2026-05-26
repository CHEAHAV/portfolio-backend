from pydantic import BaseModel

class VillageSchema(BaseModel):
    id         : str | None = None
    name       : str
    name_lc    : str
    commune_id : str
    description: str | None = None
    image      : str