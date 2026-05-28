from pydantic import BaseModel

class ProjectSchema(BaseModel):
    id         : str | None = None
    name       : str | None = None
    description: str | None = None
    duration   : str | None = None
    role       : str | None = None
    platform   : str | None = None
    challenge  : str | None = None
    project_url: str | None = None
    image      : str | None = None
    active     : bool