from icb.core.model import CoreModel, Column, String, JSONB, Integer, DateTime

class WORKFLOW_PARENT():
    id          = Column(String(64), primary_key=True)
    module_id   = Column(String(64))
    condition   = Column(JSONB)#[['Field','CoditionOperator','CoditionValue','FieldLabel']]
    description = Column(String(250), nullable=False)

class TBL_WORKFLOW(WORKFLOW_PARENT,CoreModel):
    pass

class TBL_WORKFLOW_UNAUTH(WORKFLOW_PARENT,CoreModel):
    pass

class TBL_WORKFLOW_HISTORY(WORKFLOW_PARENT,CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_WORKFLOW_DELETED(WORKFLOW_PARENT,CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

class TBL_WORKFLOW_REJECTED(WORKFLOW_PARENT,CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

class WORKFLOW_DETAIL_PARENT():
    id             = Column(String(64), primary_key=True)
    parent_id      = Column(String(64))
    role_id        = Column(String(64))
    num_of_auth    = Column(Integer, default=0)
    auth_order     = Column(Integer, default=0)
    auth_status    = Column(String(50))
    role_condition = Column(JSONB)                         #[['Field','CoditionOperator','CoditionValue','FieldLabel']]

class TBL_WORKFLOW_DETAIL(WORKFLOW_DETAIL_PARENT,CoreModel):
    pass

class TBL_WORKFLOW_DETAIL_UNAUTH(WORKFLOW_DETAIL_PARENT,CoreModel):
    pass

class TBL_WORKFLOW_DETAIL_HISTORY(WORKFLOW_DETAIL_PARENT,CoreModel):
    re_version = Column(Integer, default='0', primary_key=True)

class TBL_WORKFLOW_DETAIL_DELETED(WORKFLOW_DETAIL_PARENT,CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

class TBL_WORKFLOW_DETAIL_REJECTED(WORKFLOW_DETAIL_PARENT,CoreModel):
    re_version    = Column(Integer, default=0, primary_key=True)
    re_deleted_at = Column(DateTime, primary_key=True)   

