from pydantic import BaseModel

class MessageSchemas(BaseModel):
    id        : str | None = None
    first_name: str | None = None
    last_name : str | None = None
    email     : str | None = None
    subject   : str | None = None
    message   : str | None = None
    active    : bool