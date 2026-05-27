import os
import shutil
import uuid
from pathlib import Path
from urllib.parse import unquote, urlparse

import cloudinary
import cloudinary.uploader
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


def is_remote_url(value: str | None) -> bool:
    return bool(value and value.startswith(("http://", "https://")))


def media_url(value: str | None) -> str:
    return value if is_remote_url(value) else ""


def media_name(value: str | None) -> str:
    if not value:
        return ""

    path = urlparse(value).path if is_remote_url(value) else value
    return unquote(Path(path).name)


def upload_image_to_cloudinary(upload: UploadFile, folder: str) -> str:
    if not upload.filename:
        raise HTTPException(status_code=400, detail="Uploaded file has no filename")

    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME", "do4c64x7h")
    api_key = os.getenv("CLOUDINARY_API_KEY", "187482869256971")
    api_secret = os.getenv("CLOUDINARY_API_SECRET", "")

    if not cloud_name or not api_key or not api_secret:
        raise HTTPException(status_code=500, detail="Cloudinary is not configured")

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True,
    )

    source_name = Path(upload.filename).name
    public_id = f"{Path(source_name).stem or 'upload'}-{uuid.uuid4().hex}"
    prefix = os.getenv("CLOUDINARY_FOLDER_PREFIX", "portfolio").strip("/")
    cloud_folder = f"{prefix}/{folder.strip('/')}" if prefix else folder.strip("/")

    try:
        upload.file.seek(0)
        result = cloudinary.uploader.upload(
            upload.file,
            folder=cloud_folder,
            public_id=public_id,
            resource_type="image",
            overwrite=False,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload failed: {exc}") from exc

    secure_url = result.get("secure_url")
    if not secure_url:
        raise HTTPException(status_code=500, detail="Cloudinary upload did not return a secure URL")

    return secure_url
