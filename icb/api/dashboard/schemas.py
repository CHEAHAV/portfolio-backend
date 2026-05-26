from .models import *
from pydantic import BaseModel, Field

class DashboardSchema(BaseModel):
    id  : str
    name: str = Field(default=None, title="Name", min_length=1, max_length=100)

class DashboardItemSchema(BaseModel):
    id            : str | None = None
    name          : str | None = None
    dashboard_card: str | None = None
    width         : int
    order         : int = 0

class DashboardItemListSchema(BaseModel):
    dashboards_item: list[DashboardItemSchema] | None = None