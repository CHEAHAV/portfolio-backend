from datetime import timezone, datetime
from pydantic import validator
from pydantic import BaseModel
from typing import Optional


class ApiTokenSchema(BaseModel):
    id: str | None = None
    name: str
    origins: list[str] | None = None
    expires_at: Optional[datetime] = None

    @validator('expires_at', pre=True)
    def validate_expires_at(cls, v):
        if v is not None:
            # Parse date string if it lacks time information
            if isinstance(v, str):
                try:
                    v = datetime.fromisoformat(v)
                except ValueError:
                    raise ValueError("Invalid datetime format. Use ISO 8601 format.")
            
            # Ensure the datetime is timezone-aware
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
            
            if v <= datetime.now(timezone.utc):
                raise ValueError("Expiration date must be in the future")
        return v
