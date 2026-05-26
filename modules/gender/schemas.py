from pydantic import BaseModel

class GenderSchema(BaseModel):
    id            : str | None = None
    description   : str
    description_lc: str
    order         : int | None = None
    icon          : str | None = None
