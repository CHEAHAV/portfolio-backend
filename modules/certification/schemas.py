from datetime import date

from pydantic import BaseModel

class CertificationSchema(BaseModel):
    id             : str | None = None
    name           : str | None = None
    title          : str | None = None
    issuer         : str | None = None
    date_earned    : date | None = None
    credential_id  : str | None = None
    certificate_url: str | None = None
    icon           : str | None = None
    active         : bool