from pydantic import BaseModel

class TeachStackSchema(BaseModel):
    id         : str | None = None
    name_left  : str | None = None
    image_left : str | None = None
    name_right : str | None = None
    image_right: str | None = None
    active     : bool