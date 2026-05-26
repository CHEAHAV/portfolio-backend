from pydantic import BaseModel

class SocialSchema(BaseModel):
    id         : str | None = None
    name       : str | None = None
    icon       : str | None = None
    active     : bool