from typing import List

from icb.lib.render_api import render_detail
from main import app, Body
from icb.core.crud_api import *
from .schemas import *
from datetime import datetime
from icb.core.security import get_current_active_user


class NOTIFICATION_CRUD_API(CRUDAPI):
    query_fields = ['id']

    def get_header(self):
        return [
            {"field": "id", "text": "ID"},
            {"field": "module_id", "text": "Module ID"},
            {"field": "notify_type", "text": "Notify Type"},
            {"field": "data", "text": "Data"},
        ]


@app.get("/api/v1/wb/notifications/unread_count", tags=['Notification'])
async def get_unread_count_notifications(current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Retrieve the count of unread notifications for the authenticated user.

    Args:
        current_user (Annotated[User, Depends(get_current_active_user)]): The currently authenticated user.

    Returns:
        dict: A dictionary containing the status, message, unread notifications count, and timestamp.
    """
    data_unread = db.query(TBL_USER_NOTIFICATION.id). \
        filter((TBL_USER_NOTIFICATION.viewed_at.is_(None)) | (TBL_USER_NOTIFICATION.viewed_at == '')). \
        filter(TBL_USER_NOTIFICATION.user_id == current_user.id). \
        count()

    return {
        "ok": True,
        "status": 200,
        "title": "Notification",
        "data": {
            "unread_count": data_unread
        },
        "message": "Unread notifications count retrieved successfully"
    }


@app.put("/api/v1/wb/notifications/mark_reads", tags=['Notification'])
async def mark_reads_notifications(
        body: NotificationMarkReadSchema,
        current_user: Annotated[User, Depends(get_current_active_user)],
        mark_all: bool = False,
):
    """
    Mark notifications as read for the authenticated user.

    Args:
        body (NotificationMarkReadSchema): The schema containing the list of notification IDs to mark as read.
        current_user (Annotated[User, Depends(get_current_active_user)]): The currently authenticated user.
        mark_all (bool, optional): Whether to mark all notifications as read. Defaults to False.

    Raises:
        HTTPException: If the notification_ids list is empty and mark_all is False.

    Returns:
        dict: A dictionary containing the status and message of the operation.
    """
    if not mark_all and not body.notification_ids:
        raise HTTPException(
            status_code=400, detail="notification_ids is required.")

    data_update = {
        "viewed_at": datetime.now(),
        "re_updated_at": datetime.now(),
        "re_updated_by": current_user.id
    }

    query = db.query(TBL_USER_NOTIFICATION).filter(
        TBL_USER_NOTIFICATION.user_id == current_user.id)
    if mark_all:
        query = query.filter(TBL_USER_NOTIFICATION.viewed_at.is_(
            None) | (TBL_USER_NOTIFICATION.viewed_at == ''))
    else:
        query = query.filter(
            TBL_USER_NOTIFICATION.notification_id.in_(body.notification_ids))

    try:
        query.update(data_update)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "ok": True,
        "status": 200,
        "title": "Notification",
        "message": "Notifications marked as read successfully"
    }


@app.get("/api/v1/wb/notifications/me", tags=['Notification'])
async def list_notifications_authenticated_user(current_user: Annotated[User, Depends(get_current_active_user)],
                                                page: int = 1, size: int = 10, only_unread: bool = False):
    """
    Retrieve a paginated list of notifications for the authenticated user.

    Args:
        current_user (Annotated[User, Depends(get_current_active_user)]): The currently authenticated user.
        page (int, optional): The page number to retrieve. Defaults to 1.
        size (int, optional): The number of notifications per page. Defaults to 10.
        only_unread (bool, optional): Whether to retrieve only unread notifications. Defaults to False.

    Returns:
        dict: A dictionary containing the status, message, list of notifications, and pagination metadata.
    """
    offset = (page - 1) * size
    query = db.query(
        TBL_NOTIFICATION.id,
        TBL_NOTIFICATION.module_id,
        TBL_NOTIFICATION.data,
        TBL_NOTIFICATION.notify_type,
        TBL_USER_NOTIFICATION.viewed_at,
        TBL_USER_NOTIFICATION.re_created_at,
        TBL_USER_NOTIFICATION.re_updated_at,
        TBL_MODULE.url.label('module_url'),
    ).join(
        TBL_USER_NOTIFICATION, TBL_USER_NOTIFICATION.notification_id == TBL_NOTIFICATION.id
    ).\
        join(TBL_MODULE, TBL_MODULE.id == TBL_NOTIFICATION.module_id).\
        filter(
        TBL_USER_NOTIFICATION.user_id == current_user.id
    )

    if only_unread:
        query = query.filter(TBL_USER_NOTIFICATION.viewed_at.is_(
            None) | (TBL_USER_NOTIFICATION.viewed_at == ''))

    notifications = query.order_by(TBL_USER_NOTIFICATION.id.desc()).offset(offset).limit(size).all()

    total_notifications = query.count()

    total_pages = math.ceil(total_notifications / size)

    formatted_notifications = [
        {
            "id": n.id,
            "module_id": n.module_id,
            "module_url": n.module_url,
            "notify_type": n.notify_type, 
            "data": n.data,
            "re_created_at": n.re_created_at,
            "re_updated_at": n.re_updated_at,
            "is_seen": n.viewed_at is not None and n.viewed_at != ''
        } for n in notifications
    ]

    return {
        "ok": True,
        "status": 200,
        "title": "Notification",
        "message": "Data was retrieved successfully",
        "data": {
            "lists": formatted_notifications,
            "meta_data": {
                "total": total_notifications,
                "total_page": total_pages,
                "current_page": page,
                "size": size
            }
        }
    }


@app.delete("/api/v1/wb/notifications/remove", tags=['Notification'])
async def remove_notifications(
    current_user: Annotated[User, Depends(get_current_active_user)],
    notification_id: str = None,
    remove_all: bool = False
):
    """
    Remove notifications for the authenticated user.

    Args:
        current_user (Annotated[User, Depends(get_current_active_user)]): The currently authenticated user.
        notification_id (str, optional): The ID of the notification to remove. Defaults to None.
        remove_all (bool, optional): Whether to remove all notifications. Defaults to False.

    Returns:
        dict: A dictionary containing the status and message of the operation.
    """
    try:
        if not remove_all and not notification_id:
            raise HTTPException(
                status_code=400, detail="notification_id is required.")

        query = db.query(TBL_USER_NOTIFICATION).filter(
            TBL_USER_NOTIFICATION.user_id == current_user.id
        )

        if notification_id and not remove_all:
            query = query.filter(
                TBL_USER_NOTIFICATION.notification_id == notification_id)

        count = query.count()

        if count == 0:
            raise HTTPException(
                status_code=404, detail="No notifications found to remove.")

        if remove_all or count != 0:
            query.delete(synchronize_session=False)
            db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "ok": True,
        "status": 200,
        "title": "Notification",
        "message": "Notification(s) removed successfully"
    }


@app.get("/api/v1/wb/notifications/{notification_id}/view", tags=['Notification'])
async def get_user_notification_by_notify_id(notification_id: str,
                                             current_user: Annotated[User, Depends(get_current_active_user)]):
    """
    Retrieve a specific notification for the authenticated user by notification ID.

    Args:
        notification_id (str): The ID of the notification to retrieve.
        current_user (Annotated[User, Depends(get_current_active_user)]): The currently authenticated user.

    Returns:
        dict: A dictionary containing the status, message, and the notification data.
    """
    data = db.query(
        TBL_NOTIFICATION.id,
        TBL_NOTIFICATION.module_id,
        TBL_NOTIFICATION.data,
        TBL_USER_NOTIFICATION.viewed_at,
        TBL_USER_NOTIFICATION.re_created_at,
        TBL_USER_NOTIFICATION.re_updated_at,
        TBL_MODULE.url.label('module_url'),
    ).join(
        TBL_USER_NOTIFICATION, TBL_USER_NOTIFICATION.notification_id == TBL_NOTIFICATION.id
    ).join(
        TBL_MODULE, TBL_MODULE.id == TBL_NOTIFICATION.module_id
    ).\
        filter(
        TBL_USER_NOTIFICATION.user_id == current_user.id,
        TBL_USER_NOTIFICATION.notification_id == notification_id
    ).first()

    if not data:
        raise HTTPException(
            status_code=404, detail="User notification not found")

    formatted_notification = {
        "id": data.id,
        "module_id": data.module_id,
        "module_url": data.module_url,
        "data": data.data,
        "re_created_at": data.re_created_at,
        "re_updated_at": data.re_updated_at,
        "is_seen": data.viewed_at is not None and data.viewed_at != ''
    }

    return {
        "ok": True,
        "status": 200,
        "title": "Notification",
        "message": "Data was retrieved successfully",
        "data": {
            "item": formatted_notification
        }
    }

crud = NOTIFICATION_CRUD_API(
    'Notification', 'notifications', TBL_NOTIFICATION, {}, schema=NotificationSchema)
crud.init_route()
app.include_router(crud.router, prefix="/api/v1", tags=['Notification'])
