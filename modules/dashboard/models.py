# from icb.core.model import *

# class DASHBOARDS_PARENT():
#     id   = Column(String(64), primary_key=True, index=True)
#     name = Column(String(100), nullable=False)

# class TBL_DASHBOARDS(DASHBOARDS_PARENT, CoreModel):
#     pass

# class TBL_DASHBOARDS_UNAUTH(DASHBOARDS_PARENT, CoreModel):
#     pass

# class TBL_DASHBOARDS_HISTORY(DASHBOARDS_PARENT, CoreModel):
#     re_version = Column(Integer, default='0', primary_key=True)

# class TBL_DASHBOARDS_DELETED(DASHBOARDS_PARENT, CoreModel):
#     re_version    = Column(Integer, default=0, primary_key=True)
#     re_deleted_at = Column(DateTime, primary_key=True)   

# class TBL_DASHBOARDS_REJECTED(DASHBOARDS_PARENT, CoreModel):
#     re_version    = Column(Integer, default='0', primary_key=True)
#     re_deleted_at = Column(DateTime, primary_key=True)

# class DASHBOARDS_ITEM_PARENT ():
#     id             = Column(String(64), primary_key=True, index=True)
#     parent_id      = Column(String(64), primary_key=True)
#     name           = Column(String(100))
#     dashboard_card = Column(String(100))
#     width          = Column(Integer, default=0)
#     order          = Column(Integer, default=0)

# class TBL_DASHBOARD_ITEM(DASHBOARDS_ITEM_PARENT, CoreModel):
#     pass

# class TBL_DASHBOARD_ITEM_UNAUTH(DASHBOARDS_ITEM_PARENT, CoreModel):
#     pass

# class TBL_DASHBOARD_ITEM_HISTORY(DASHBOARDS_ITEM_PARENT, CoreModel):
#     re_version = Column(Integer, default='0', primary_key=True)

# class TBL_DASHBOARD_ITEM_DELETED(DASHBOARDS_ITEM_PARENT, CoreModel):
#     re_version    = Column(Integer, default=0, primary_key=True)
#     re_deleted_at = Column(DateTime, primary_key=True)   

# class TBL_DASHBOARD_ITEM_REJECTED(DASHBOARDS_ITEM_PARENT, CoreModel):
#     re_version    = Column(Integer, default='0', primary_key=True)
#     re_deleted_at = Column(DateTime, primary_key=True)