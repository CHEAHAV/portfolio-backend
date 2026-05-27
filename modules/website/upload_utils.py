import os
import shutil
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile


def save_upload_with_unique_name(upload: UploadFile, directory: str) -> str:
    if not upload.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename")

    os.makedirs(directory, exist_ok=True)
    source_name = Path(upload.filename).name
    suffix = Path(source_name).suffix.lower()
    stem = Path(source_name).stem or "upload"
    filename = source_name
    dest = os.path.join(directory, filename)

    if os.path.exists(dest):
        filename = f"{stem}-{uuid.uuid4().hex}{suffix}"
        dest = os.path.join(directory, filename)

    with open(dest, "wb") as f:
        shutil.copyfileobj(upload.file, f)

    return filename
