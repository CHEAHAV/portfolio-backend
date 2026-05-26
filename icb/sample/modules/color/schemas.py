
from pydantic import BaseModel

class ColorSchema(BaseModel): 
    id  : str | None = None
    name: str