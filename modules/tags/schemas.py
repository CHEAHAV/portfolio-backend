from pydantic import BaseModel

class TagsSchema(BaseModel):
    id         : str | None = None
    name       : str
    description: str
    active     : bool