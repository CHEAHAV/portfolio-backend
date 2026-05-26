from pydantic import BaseModel

class SkillSchema(BaseModel):
    id         : str | None = None
    name       : str | None = None
    score      : float | None = None
    description: str | None = None
    image      : str | None = None
    active     : bool