from icb.core.model import *

# Table for menu and related table
class MENU_PARENT():
    id          = Column(String(64), primary_key=True)
    description = Column(String(64), nullable=False)
    ordering    = Column(Integer, nullable=True)

class TBL_MENU(MENU_PARENT,CoreModel):
    pass

class TBL_MENU_UNAUTH(MENU_PARENT,CoreModel):
    pass

class TBL_MENU_HISTORY(MENU_PARENT,CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_MENU_DELETED(MENU_PARENT,CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

class TBL_MENU_REJECTED(MENU_PARENT,CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)

# Table for sub menu and related tables
class SUB_MENU_PARENT():
    parent_id = Column(String(64), primary_key=True)
    label     = Column(String(100), nullable=False)
    main_id   = Column(String(64))
    module_id = Column(String(64))
    icon      = Column(String(64))
    url       = Column(String(150))
    type      = Column(String(15), nullable=True) # permission label, standard, or custom 
    ordering  = Column(Integer, nullable=True)
    
class TBL_SUB_MENU(SUB_MENU_PARENT,CoreModel):
    pass

class TBL_SUB_MENU_UNAUTH(SUB_MENU_PARENT,CoreModel):
    pass

class TBL_SUB_MENU_HISTORY(SUB_MENU_PARENT,CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_SUB_MENU_DELETED(SUB_MENU_PARENT,CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

class TBL_SUB_MENU_REJECTED(SUB_MENU_PARENT,CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)



class MENU_ITEM_PARENT():
    id        = Column(String(64), primary_key=True)
    type      = Column(String(15), nullable=True) # label, standard, or custom
    label     = Column(String(100), nullable=False)
    module_id = Column(String(64))
    url       = Column(String(150))
    icon      = Column(String(64))
    
class TBL_MENU_ITEM(MENU_ITEM_PARENT,CoreModel):
    pass

class TBL_MENU_ITEM_UNAUTH(MENU_ITEM_PARENT,CoreModel):
    pass

class TBL_MENU_ITEM_HISTORY(MENU_ITEM_PARENT,CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_MENU_ITEM_DELETED(MENU_ITEM_PARENT,CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

class TBL_MENU_ITEM_REJECTED(MENU_ITEM_PARENT,CoreModel):
    re_version    = Column(Integer, default='0', primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)

