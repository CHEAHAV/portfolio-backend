from pydantic import BaseModel

class StudySchema(BaseModel):
    id         : str | None = None
    title      : str | None = None
    sub_title  : str | None = None
    description: str | None = None
    date       : str | None = None
    active     : bool