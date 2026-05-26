

from pydantic import BaseModel


class AnimalSchema(BaseModel): 
    id            : str | None = None
    name          : str
    number_of_leg : int
    number_of_hand: int
    gender_id     : str | None = None
    color_id      : str | None = None
    description   : str | None = None


class AnimalChildSchema(BaseModel): 
    id            : str | None = None
    name          : str
    gender_id     : str | None = None

class AnimalSubListSchema(BaseModel): 
    child : list[AnimalChildSchema]| None = None