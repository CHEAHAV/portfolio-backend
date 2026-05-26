import re


def generate_prefixed_id(db, models, prefix, width=8):
    if not isinstance(models, (list, tuple)):
        models = [models]

    max_id = 0
    pattern = re.compile(rf"{re.escape(prefix)}(\d+)")

    for model in models:
        rows = db.query(model.id).filter(model.id.like(f"{prefix}%")).all()
        for row in rows:
            match = pattern.fullmatch(row[0] or "")
            if match:
                max_id = max(max_id, int(match.group(1)))

    return f"{prefix}{max_id + 1:0{width}d}"


def assign_prefixed_id(crud, models, prefix, width=8):
    if not crud.item.get("id"):
        crud.item["id"] = generate_prefixed_id(crud.db, models, prefix, width)
