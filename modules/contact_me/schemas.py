from pydantic import BaseModel

class ContactMeSchema(BaseModel):
    id         : str | None = None
    name       : str | None = None
    description: str | None = None
    icon       : str | None = None
    active     : bool