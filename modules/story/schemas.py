from pydantic import BaseModel

class StorySchema(BaseModel):
    id         : str | None = None
    title      : str | None = None
    description: str | None = None
    icon_name  : str | None = None
    icon       : str | None = None
    active     : bool