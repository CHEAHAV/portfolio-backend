ACTIVE_BOOKING_STATUSES = ("BOOKED", "CONFIRMED")
MODULE_NAME = "Meeting Booking"
MODULE_SLUG = "meeting-bookings"
MODULE_TAGS = ["Meeting Booking"]

QUERY_FIELDS = ["title", "room_id", "status"]

LIST_HEADERS = [
    {"field": "id", "text": "ID"},
    {"field": "room_id", "text": "Room ID"},
    {"field": "name", "model": None, "label": "room_name", "text": "Room Name"},
    {"field": "title", "text": "Title"},
    {"field": "organizer_user_id", "text": "Organizer User ID"},
    {"field": "start_at", "text": "Start At"},
    {"field": "end_at", "text": "End At"},
    {"field": "attendee_count", "text": "Attendees"},
    {"field": "status", "text": "Status"},
    {"field": "purpose", "text": "Purpose"},
]
