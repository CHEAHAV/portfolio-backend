from icb.core.model import *

class API_TOKEN_PARENT():
    id              = Column(String(64), primary_key=True, index=True)
    name            = Column(String(64))
    token_hash      = Column(String, index=True)
    backup_key      = Column(String)
    user_id         = Column(String(64), index=True)
    scope           = Column(String(255)) # full_access
    origins         = Column(String) # store as text with comma separated values
    expires_at      = Column(DateTime)
    last_used_at    = Column(DateTime)
    revoked         = Column(Boolean, default=False)
    
class TBL_API_TOKEN(API_TOKEN_PARENT,CoreModel):
    pass
