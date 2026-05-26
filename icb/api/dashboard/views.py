import pytz

from ..user.models import TBL_USER
from main import app
from icb.core.crud_api import *
from .models import *
from .schemas import *
from icb.core.security import User, get_current_active_user
from fastapi import Depends
from icb.lib.render_api import *
from decimal import Decimal
from datetime import datetime, timedelta, timezone


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
    # Purchase order overview
    suppliers = db.query(TBL_SUPPLIER). \
        filter(TBL_SUPPLIER.branch_id == current_user.working_branch). \
        count()
    purchase_orders = db.query(TBL_PURCHASE). \
        filter(TBL_PURCHASE.branch_id == current_user.working_branch). \
        count()

    po_amount = db.query(func.sum(TBL_PURCHASE.total_cost_include_tax)). \
        filter(TBL_PURCHASE.branch_id == current_user.working_branch). \
        scalar() or 0

    # Sale order overview
    sale_orders = db.query(TBL_SALE_ORDER). \
        filter(TBL_SALE_ORDER.branch_id == current_user.working_branch). \
        count()

    so_amount = db.query(func.sum(TBL_SALE_ORDER.total_price_include_tax)). \
        filter(TBL_SALE_ORDER.branch_id == current_user.working_branch). \
        scalar() or 0
        
    outlets = db.query(TBL_CUSTOMER_RECEIVING_ADDRESS). \
        filter(TBL_CUSTOMER_RECEIVING_ADDRESS.branch_id == current_user.working_branch). \
        count()

    # Invoice and collection
    pending_invoices = db.query(TBL_SALE_PAYMENT). \
        filter(TBL_SALE_PAYMENT.invoice_date.is_(None)). \
        count()

    uncollected_invoices = db.query(TBL_SALE_PAYMENT). \
        filter(TBL_SALE_PAYMENT.status.in_(["Unpaid", "Partial Paid"])). \
        count()

    unauth_records = get_unauthorized_records(current_user)

    user_online_data = get_users_online(current_user)

    store_inbound = get_num_inbound_of_status(db, current_user)
    store_outbound = get_num_outbound_of_status(db, current_user)

    data = {
        "purchase_order": {
            "supplier": suppliers,
            "purchase_order": purchase_orders,
            "amount": po_amount,
            "icon": "ri-shopping-cart-line",
        },
        "sale_order": {
            "outlet": outlets,
            "sale_order": sale_orders,
            "amount": so_amount,
            "icon": "ri-shopping-cart-line",
        },
        "collection": {
            "pending_invoices": pending_invoices,
            "uncollected_invoices": uncollected_invoices,
            "icon": "ri-shopping-cart-line",
        },
        "unauth_records": {
            "icon": "ri-shopping-cart-line",
            "data": unauth_records,
        },
        "users_online": {
            "icon": "ri-shopping-cart-line",
            "data": user_online_data,
        },
        "inbound": {
            "icon": "ri-shopping-cart-line",
            "data": store_inbound,
        },
        "outbound": {
            "icon": "ri-shopping-cart-line",
            "data": store_outbound,
        }
    }

    return_data = dict(
        status=True,
        title='Dashboard',
        message='Dashboard',
        module='dashboard',
        data=data,
        total_record=100,
        page=1,
        size=100,
    )

    return return_data


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
