from icb.core.model import CoreModel
from sqlalchemy import Column, String, Integer, DateTime

class ANIMAL_PARENT(): 
    id             = Column(String(42), primary_key=True)
    name           = Column(String(100), nullable=False)
    number_of_leg  = Column(Integer, nullable=False, default=0)
    number_of_hand = Column(Integer, nullable=False, default=0)
    gender_id      = Column(String(42))
    color_id       = Column(String(42))
    description    = Column(String(255))
    

class TBL_ANIMAL(ANIMAL_PARENT, CoreModel): 
    pass

class TBL_ANIMAL_UNAUTH(ANIMAL_PARENT, CoreModel): 
    pass

class TBL_ANIMAL_HISTORY(ANIMAL_PARENT, CoreModel): 
    re_version = Column(Integer, default=0, primary_key=True)

class TBL_ANIMAL_DELETED(ANIMAL_PARENT, CoreModel): 
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)

class TBL_ANIMAL_REJECTED(ANIMAL_PARENT,CoreModel): 
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)


class ANIMAL_CHILD_PARENT(): 
    id        = Column(String(42), primary_key=True)
    parent_id = Column(String(42), nullable=False)
    name      = Column(String(100), nullable=False)
    gender_id = Column(String(42))

class TBL_ANIMAL_CHILD(ANIMAL_CHILD_PARENT, CoreModel): 
    pass

class TBL_ANIMAL_CHILD_UNAUTH(ANIMAL_CHILD_PARENT, CoreModel): 
    pass

class TBL_ANIMAL_CHILD_HISTORY(ANIMAL_CHILD_PARENT, CoreModel): 
    re_version = Column(Integer, default=0, primary_key=True)

class TBL_ANIMAL_CHILD_DELETED(ANIMAL_CHILD_PARENT, CoreModel): 
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)

class TBL_ANIMAL_CHILD_REJECTED(ANIMAL_CHILD_PARENT,CoreModel): 
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)    