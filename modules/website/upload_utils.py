import os
import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile

BASE_DIR = Path(__file__).resolve().parents[2]


def resolve_upload_dir(directory: str) -> Path:
    path = Path(directory)
    return path if path.is_absolute() else BASE_DIR / path


def save_upload_with_unique_name(upload: UploadFile, directory: str) -> str:
    if not upload.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename")

    upload_dir = resolve_upload_dir(directory)
    os.makedirs(upload_dir, exist_ok=True)
    source_name = Path(upload.filename).name
    suffix = Path(source_name).suffix.lower()
    stem = Path(source_name).stem or "upload"
    filename = source_name
    dest = upload_dir / filename

    if dest.exists():
        filename = f"{stem}-{uuid.uuid4().hex}{suffix}"
        dest = upload_dir / filename

    with open(dest, "wb") as f:
        shutil.copyfileobj(upload.file, f)

    return filename
