from sqlalchemy import Date

from icb.core.model import *

class MODULE_PARENT():
    id               = Column(String(42), primary_key=True)
    name             = Column(String(100), nullable=False)
    num_of_auth      = Column(Integer, default=0)
    url              = Column(String(150), nullable=True)
    model            = Column(String(100), nullable=True)
    mask_field       = Column(String(100), nullable=True, default='') # field_name1,field_name2,...
    list_view        = Column(String(5), default='LBB') # list all branches(LABS), list by access branches(LBABS), list by branch(LBB)
    query_list       = Column(String(5), default='LBB') # list all branches(LABS), list by access branches(LBABS), list by branch(LBB)
    enable_log       = Column(Boolean, default=False)
    log_action       = Column(String(100), nullable=True, default='ALL') # ALL C R U D VL VH VU VD VR LL LH LU LD LR EP IP P
    

class TBL_MODULE(MODULE_PARENT, CoreModel):
    pass

class TBL_MODULE_UNAUTH(MODULE_PARENT, CoreModel):
    pass

class TBL_MODULE_HISTORY(MODULE_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_MODULE_DELETED(MODULE_PARENT, CoreModel):
    re_version      = Column(Integer, default='0', primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)

class TBL_MODULE_REJECTED(MODULE_PARENT,CoreModel):
    re_version      = Column(Integer, default='0', primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)

class FORM_MODULE_PARENT():
    id               = Column(String(42), primary_key=True)
    module_id        = Column(String(42), primary_key=True)
    num_of_auth      = Column(Integer, default=0)
    list_view        = Column(String(5), default='LBB') # list all branches(LABS), list by access branches(LBABS), list by branch(LBB)
    query_list       = Column(String(5), default='LBB') # list all branches(LABS), list by access branches(LBABS), list by branch(LBB)
    

class TBL_FORM_MODULE(FORM_MODULE_PARENT, CoreModel):
    pass

class TBL_FORM_MODULE_UNAUTH(FORM_MODULE_PARENT, CoreModel):
    pass

class TBL_FORM_MODULE_HISTORY(FORM_MODULE_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_FORM_MODULE_DELETED(FORM_MODULE_PARENT, CoreModel):
    re_version      = Column(Integer, default='0', primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)

class TBL_FORM_MODULE_REJECTED(FORM_MODULE_PARENT,CoreModel):
    re_version      = Column(Integer, default='0', primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)

class MODULE_ACCESSMENT_PARENT():
    id               = Column(String(64), primary_key=True)
    name             = Column(String(50), nullable=False)

class TBL_MODULE_ACCESSMENT(MODULE_ACCESSMENT_PARENT, CoreModel):
    pass

class TBL_MODULE_ACCESSMENT_UNAUTH(MODULE_ACCESSMENT_PARENT, CoreModel):
    pass

class TBL_MODULE_ACCESSMENT_HISTORY(MODULE_ACCESSMENT_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_MODULE_ACCESSMENT_DELETED(MODULE_ACCESSMENT_PARENT, CoreModel):
    re_version      = Column(Integer, default='0', primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)

class TBL_MODULE_ACCESSMENT_REJECTED(MODULE_ACCESSMENT_PARENT,CoreModel):
    re_version      = Column(Integer, default='0', primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)

class MODULE_ACCESSMENT_ITEM_PARENT():
    id               = Column(String(64), primary_key=True)
    parent_id        = Column(String(64), nullable=False) #tbl_module_accessment
    module_id        = Column(String(64))
    num_of_record    = Column(Integer)

class TBL_MODULE_ACCESSMENT_ITEM(MODULE_ACCESSMENT_ITEM_PARENT, CoreModel):
    pass

class TBL_MODULE_ACCESSMENT_ITEM_UNAUTH(MODULE_ACCESSMENT_ITEM_PARENT, CoreModel):
    pass

class TBL_MODULE_ACCESSMENT_ITEM_HISTORY(MODULE_ACCESSMENT_ITEM_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_MODULE_ACCESSMENT_ITEM_DELETED(MODULE_ACCESSMENT_ITEM_PARENT, CoreModel):
    re_version      = Column(Integer, default='0', primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)

class TBL_MODULE_ACCESSMENT_ITEM_REJECTED(MODULE_ACCESSMENT_ITEM_PARENT,CoreModel):
    re_version      = Column(Integer, default='0', primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)

class MODULE_ASSIGNMENT_PARENT():
    id                      = Column(String(64), primary_key=True)
    module_accessment_id    = Column(String(64), nullable=False) #tbl_module_accessment
    assigned_company_id     = Column(String(64))

class TBL_MODULE_ASSIGNMENT(MODULE_ASSIGNMENT_PARENT, CoreModel):
    pass

class TBL_MODULE_ASSIGNMENT_UNAUTH(MODULE_ASSIGNMENT_PARENT, CoreModel):
    pass

class TBL_MODULE_ASSIGNMENT_HISTORY(MODULE_ASSIGNMENT_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_MODULE_ASSIGNMENT_DELETED(MODULE_ASSIGNMENT_PARENT, CoreModel):
    re_version      = Column(Integer, default='0', primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)

class TBL_MODULE_ASSIGNMENT_REJECTED(MODULE_ASSIGNMENT_PARENT,CoreModel):
    re_version      = Column(Integer, default='0', primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)





class AUTO_ID_PARENT():
    id               = Column(String(42), primary_key=True)
    module_id        = Column(String(42), primary_key=True)
    id_type          = Column(String(25), nullable=False)
    id_prefix        = Column(String(10), nullable=True)
    id_index         = Column(Integer, default=0)
    id_date_format   = Column(String(20), nullable=True)
    id_serial_length = Column(Integer, default=0)
    id_prev_date     = Column(Date, nullable=True)
    

class TBL_AUTO_ID(AUTO_ID_PARENT, CoreModel):
    pass

class TBL_AUTO_ID_UNAUTH(AUTO_ID_PARENT, CoreModel):
    pass

class TBL_AUTO_ID_HISTORY(AUTO_ID_PARENT, CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_AUTO_ID_DELETED(AUTO_ID_PARENT, CoreModel):
    re_version      = Column(Integer, default='0', primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)

class TBL_AUTO_ID_REJECTED(AUTO_ID_PARENT,CoreModel):
    re_version      = Column(Integer, default='0', primary_key=True)
    re_deleted_at   = Column(DateTime, primary_key=True)


