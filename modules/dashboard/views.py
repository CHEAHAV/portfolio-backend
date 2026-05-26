import pytz
from icb.api.user.models import TBL_USER
from ..job.models import TBL_JOB
# from ..service.models import TBL_SERVICE
# from ..event.models import TBL_EVENT
# from ..publication.models import TBL_PUBLICATION
from main import app
from icb.core.crud_api import *
from icb.api.dashboard.models import *
from .schemas import *
from icb.core.security import User, get_current_active_user
from fastapi import Depends
from icb.lib.render_api import *
from icb.api.system_date.models import TBL_SYSTEM_DATE
from icb.core.db_session import get_db
from sqlalchemy import func
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date, datetime, timedelta, timezone


class DASHBOARD_CRUD_API(CRUDAPI):
    def get_header(self):
        return [
            {"field": "id", "text": "ID"},
            {"field": "name", "text": "Name"}
        ]

    def get_header_sub(self):
        return {
            'dashboards_item': [
                {'field': 'id', 'text': 'ID'},
                {'field': 'name', 'text': 'Name'},
                {'field': 'dashboard_card', 'text': 'Dashboard Card'},
                {'field': 'width', 'text': 'Width'},
                {'field': 'order', 'text': 'Order'}
            ]
        }

    def check_validation(self):
        sub_item = self.sub_item.get('dashboards_item', [])

        errors = {}
        count = 0
        for item in sub_item:
            error = {}
            count += 1

            width = Decimal(item.get('width', 0))

            if not (1 <= width <= 12):
                error.update({'width': 'Width must be between 1 and 12.'})

            if error:
                errors.update({count: error})

        if errors:
            raise ValueError({'dashboards_item': errors})

        return True, ''

    def before_save(self):
        self.check_validation()
        return True,


crud = DASHBOARD_CRUD_API('Dashboard', 'dashboard',
                          TBL_DASHBOARDS,
                          {
                              'dashboards_item': TBL_DASHBOARD_ITEM,
                          },
                          schema=DashboardSchema,
                          sub_schema=DashboardItemListSchema
                          )

crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Dashboard'])


@app.post("/api/v1/wb/get-dashboard", tags=['Dashboard'])
async def dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):    
    job_count         = db.query(func.count(TBL_JOB.id)).scalar() or 0
    service_count     = db.query(func.count(TBL_SERVICE.id)).scalar() or 0
    event_count       = db.query(func.count(TBL_EVENT.id)).scalar() or 0
    publication_count = db.query(func.count(TBL_PUBLICATION.id)).scalar() or 0

    # data = {
    #     "job_application":{
    #         "total": job_count,
    #           # "completed":2,   
    #     },
    #     "services":{
    #         "service": service_count,
    #     },
    #     "events":{
    #         "event": event_count,
    #     },
    #     "publications":{
    #         "publication": publication_count,
    #     },
    # }
    # return_data = dict(
    #     status       = True,
    #     title        = 'Dashboard',
    #     message      = 'Dashboard',
    #     module       = 'dashboard',
    #     data         = data,
    #     total_record = 100,
    #     page         = 1,
    #     size         = 100,
    # )

    # return return_data

@app.get("/api/v1/wb/get-current-system-date", tags=['Dashboard'])
async def get_current_system_date(db: Session = Depends(get_db)):
    system_date_obj = db.query(TBL_SYSTEM_DATE).first()
    current_system_date = system_date_obj.current_system_date if system_date_obj else date.today()
    return current_system_date


def get_users_online(current_user):
    """
    Retrieve a list of users who have been online within the last 10 minutes, excluding the current user.
    Args:
        current_user (User): The current user object, which includes the user's ID and working branch.
    Returns:
        list: A list of dictionaries, each containing user information and the number of minutes since their last activity.
        Each dictionary contains the following keys:
            - id (int): The user's ID.
            - email (str): The user's email address.
            - last_activity_at (datetime): The timestamp of the user's last activity.
            - first_name (str): The user's first name.
            - last_name (str): The user's last name.
            - minutes_since_last_activity (float): The number of minutes since the user's last activity.
    """
    local_tz = pytz.timezone("Asia/Phnom_Penh")
    today = datetime.now(timezone.utc)
    five_minutes_ago = today - timedelta(minutes=10)
    users_online = db.query(
        TBL_USER.id,
        TBL_USER.email,
        TBL_USER.last_activity_at,
        TBL_USER.first_name,
        TBL_USER.last_name,
    ).filter(
        TBL_USER.last_activity_at >= five_minutes_ago
    ).filter(
        TBL_USER.branch_id == current_user.working_branch
    ).filter(TBL_USER.id != current_user.id).all()

    user_online_data = []
    for user in users_online:
        last_activity = user.last_activity_at

        if last_activity.tzinfo is None:
            last_activity = local_tz.localize(last_activity)
        last_activity = last_activity.astimezone(timezone.utc)

        minutes_since_last_activity = (
            today - last_activity).total_seconds() / 60
        user_online_data.append(
            {**user._asdict(), "minutes_since_last_activity": minutes_since_last_activity})

    return user_online_data
