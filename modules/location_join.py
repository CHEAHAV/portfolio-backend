from sqlalchemy import String, cast, func, or_


def prefixed_id_join(parent_id, child_id, prefix, width=8):
    child_id_text = cast(child_id, String)
    parent_id_text = cast(parent_id, String)

    return or_(
        parent_id == child_id,
        parent_id_text == func.concat(prefix, func.lpad(child_id_text, width, "0")),
        child_id_text == func.concat(prefix, func.lpad(parent_id_text, width, "0")),
    )


def prefixed_id_filter(model, value, prefix, width=8):
    if not value:
        return model.id == value

    value = str(value)
    values = {value}

    if value.startswith(prefix):
        suffix = value[len(prefix):].lstrip("0")
        if suffix:
            values.add(suffix)
    elif value.isdigit():
        values.add(f"{prefix}{int(value):0{width}d}")

    return model.id.in_(values)


def lookup_name(db, model, value, prefix=None):
    if not value:
        return ""

    query = db.query(model)
    if prefix:
        query = query.filter(prefixed_id_filter(model, value, prefix))
    else:
        query = query.filter(model.id == value)

    obj = query.first()
    return obj.name if obj else ""
