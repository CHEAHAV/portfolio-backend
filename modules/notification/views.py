import math
import uuid
from fastapi import Body, Depends, Query
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import Session
from icb.core.db_session import engine, get_db
from icb.core.security import User, get_current_active_user
from main import app
from icb.api.notification.models import TBL_NOTIFICATION


TBL_NOTIFICATION.__table__.create(bind=engine, checkfirst=True)


def _get_user_id(current_user):
    return (
        getattr(current_user, "id", None)
        or getattr(current_user, "user_id", None)
        or getattr(current_user, "sub", None)
    )


def _get_company_id(current_user):
    return (
        getattr(current_user, "token_working_company_id", None)
        or getattr(current_user, "working_company_id", None)
        or getattr(current_user, "company_id", None)
        or "SYSTEM"
    )


def _format_notification(row):
    data = row.data or {}

    created_at = getattr(row, "re_created_at", None)

    return {
        "id": row.id,
        "module": data.get("module"),
        "module_url": data.get("module_url"),
        "action": data.get("action"),
        "record_id": data.get("record_id"),
        "record_type": data.get("type"),
        "data": data,
        "is_seen": bool(data.get("is_seen")),
        "time": created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else "",
    }


@app.post("/api/v1/wb/notifications", tags=["Notification"])
async def create_notification(
    body: dict = Body(default={}),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    action = body.get("action") or "changed"
    module = body.get("module") or "Record"
    module_url = body.get("module_url") or module
    record_id = body.get("record_id")
    record_type = body.get("record_type") or "AUTH"

    title = body.get("title") or f"{module} {action}"
    description = body.get("description") or f"{module} was {action}"

    data = {
        "title": title,
        "description": description,
        "type": record_type,
        "record_id": record_id,
        "module": module,
        "module_url": module_url,
        "action": action,
        "user_id": _get_user_id(current_user),
        "is_seen": False,
    }

    row = TBL_NOTIFICATION(
        id=str(uuid.uuid4()),
        module_id=record_id,
        notify_type=action[:25],
        data=data,
        company_id=_get_company_id(current_user),
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "ok": True,
        "status": 200,
        "title": "Notification",
        "message": "Notification created",
        "data": _format_notification(row),
        "error": {},
    }


@app.get("/api/v1/wb/notifications/me", tags=["Notification"])
async def get_my_notifications(
    record_type: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    user_id = _get_user_id(current_user)
    rows = db.query(TBL_NOTIFICATION).order_by(TBL_NOTIFICATION.re_created_at.desc()).all()
    rows = [
        row for row in rows
        if (row.data or {}).get("user_id") == user_id
        and (not record_type or (row.data or {}).get("type") == record_type)
    ]
    total = len(rows)
    rows = rows[(page - 1) * size:(page - 1) * size + size]
    total_pages = math.ceil(total / size) if size else 1

    return {
        "ok": True,
        "status": 200,
        "title": "Notification",
        "message": "Data retrieved successfully",
        "data": {
            "lists": [_format_notification(row) for row in rows],
            "meta_data": {
                "total": total,
                "total_page": total_pages,
                "current_page": page,
                "size": size,
            },
        },
        "error": {},
    }


@app.get("/api/v1/wb/notifications/unread_count", tags=["Notification"])
async def get_unread_notification_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    user_id = _get_user_id(current_user)
    rows = db.query(TBL_NOTIFICATION).all()
    unread_count = sum(
        1 for row in rows
        if (row.data or {}).get("user_id") == user_id and not (row.data or {}).get("is_seen")
    )
    return {
        "ok": True,
        "status": 200,
        "title": "Notification",
        "message": "Data retrieved successfully",
        "data": {"unread_count": unread_count},
        "error": {},
    }


@app.put("/api/v1/wb/notifications/mark_reads", tags=["Notification"])
async def mark_notifications_read(
    mark_all: bool = Query(default=False),
    body: dict = Body(default={}),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    user_id = _get_user_id(current_user)
    notification_ids = body.get("notification_ids") or []
    rows = db.query(TBL_NOTIFICATION).all()
    for row in rows:
        data = row.data or {}
        if data.get("user_id") != user_id:
            continue
        if not mark_all and row.id not in notification_ids:
            continue
        data["is_seen"] = True
        row.data = data
        flag_modified(row, "data")
    db.commit()

    return {
        "ok": True,
        "status": 200,
        "title": "Notification",
        "message": "Notifications marked as read",
        "data": {},
        "error": {},
    }


@app.delete("/api/v1/wb/notifications/remove", tags=["Notification"])
async def remove_notifications(
    notification_id: str | None = Query(default=None),
    remove_all: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    user_id = _get_user_id(current_user)
    rows = db.query(TBL_NOTIFICATION).all()
    for row in rows:
        data = row.data or {}
        if data.get("user_id") != user_id:
            continue
        if remove_all or row.id == notification_id:
            db.delete(row)
    db.commit()

    return {
        "ok": True,
        "status": 200,
        "title": "Notification",
        "message": "Notifications removed",
        "data": {},
        "error": {},
    }
