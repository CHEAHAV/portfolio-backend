def empty_new_response(title):
    return {
        "ok": True,
        "status": 200,
        "title": title,
        "message": "Data retrieved successfully",
        "data": {
            "item": {},
            "sub_items": {},
        },
        "error": {},
    }
