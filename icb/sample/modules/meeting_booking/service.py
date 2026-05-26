from icb.lib.meeting_room import time_ranges_overlap, validate_booking_window

from modules.meeting_room.models import TBL_MEETING_ROOM

from .constants import ACTIVE_BOOKING_STATUSES, LIST_HEADERS
from .models import TBL_MEETING_BOOKING


def get_meeting_booking_headers():
    headers = []
    for header in LIST_HEADERS:
        item = dict(header)
        if item.get("label") == "room_name":
            item["model"] = TBL_MEETING_ROOM
        headers.append(item)
    return headers


def validate_meeting_booking(db, item, current_user, booking_id=None):
    start_at = item.get("start_at")
    end_at = item.get("end_at")
    valid, message = validate_booking_window(start_at, end_at)
    if not valid:
        return False, {"end_at": message}

    room = db.query(TBL_MEETING_ROOM).filter(
        TBL_MEETING_ROOM.id == item.get("room_id"),
        TBL_MEETING_ROOM.company_id == current_user.token_working_company_id,
    ).first()
    if not room:
        return False, {"room_id": "Meeting room does not exist"}
    if not room.is_active:
        return False, {"room_id": "Meeting room is inactive"}
    if item.get("attendee_count", 0) > room.capacity:
        return False, {"attendee_count": "Attendee count cannot exceed room capacity"}

    query = db.query(TBL_MEETING_BOOKING).filter(
        TBL_MEETING_BOOKING.room_id == item.get("room_id"),
        TBL_MEETING_BOOKING.company_id == current_user.token_working_company_id,
        TBL_MEETING_BOOKING.status.in_(ACTIVE_BOOKING_STATUSES),
    )
    if booking_id:
        query = query.filter(TBL_MEETING_BOOKING.id != booking_id)

    for booking in query.all():
        if time_ranges_overlap(start_at, end_at, booking.start_at, booking.end_at):
            return False, {"start_at": "Meeting room is already booked for this time range"}

    if not item.get("organizer_user_id"):
        item["organizer_user_id"] = current_user.id

    return True, ""
