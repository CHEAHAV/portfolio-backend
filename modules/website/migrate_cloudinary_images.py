from pathlib import Path
from types import SimpleNamespace

from icb.core.db_session import SessionLocal
from modules.certification.models import TBL_CERTIFICATION
from modules.commune.models import TBL_COMMUNE
from modules.contact_me.models import TBL_CONTACT_ME
from modules.country.models import TBL_COUNTRY
from modules.department.models import TBL_DEPARTMENT
from modules.district.models import TBL_DISTRICT
from modules.info.models import TBL_INFO
from modules.mycore.models import TBL_MY_CORE
from modules.province.models import TBL_PROVINCE
from modules.project.models import TBL_PROJECT
from modules.skill.models import TBL_SKILL
from modules.social.models import TBL_SOCIAL
from modules.story.models import TBL_STORY
from modules.teach_stack.models import TBL_TEACH_STACK
from modules.village.models import TBL_VILLAGE
from modules.website.upload_utils import is_remote_url, upload_image_to_cloudinary

BASE_DIR = Path(__file__).resolve().parents[2]

IMAGE_FIELDS = [
    (TBL_CERTIFICATION, "icon", "Certification"),
    (TBL_COMMUNE, "image", "Commune"),
    (TBL_CONTACT_ME, "icon", "ContactMe"),
    (TBL_COUNTRY, "image", "Country"),
    (TBL_DEPARTMENT, "image", "Department"),
    (TBL_DISTRICT, "image", "District"),
    (TBL_INFO, "image", "Info"),
    (TBL_MY_CORE, "image", "MyCore"),
    (TBL_PROVINCE, "image", "Province"),
    (TBL_PROJECT, "image", "Project"),
    (TBL_SKILL, "image", "Skill"),
    (TBL_SOCIAL, "icon", "Social"),
    (TBL_STORY, "icon", "Story"),
    (TBL_TEACH_STACK, "image_left", "TeachStack"),
    (TBL_TEACH_STACK, "image_right", "TeachStack"),
    (TBL_VILLAGE, "image", "Village"),
]


def upload_local_file(path: Path, folder: str) -> str:
    with path.open("rb") as file_obj:
        upload = SimpleNamespace(filename=path.name, file=file_obj)
        return upload_image_to_cloudinary(upload, folder)


def migrate_images() -> None:
    db = SessionLocal()
    migrated = 0
    missing = []

    try:
        for model, field, folder in IMAGE_FIELDS:
            rows = db.query(model).all()
            for row in rows:
                value = getattr(row, field, None)
                if not value or is_remote_url(value):
                    continue

                path = BASE_DIR / "static" / "images" / folder / value
                if not path.exists():
                    missing.append(f"{model.__name__}.{field}:{row.id}:{value}")
                    continue

                setattr(row, field, upload_local_file(path, folder))
                migrated += 1

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    print(f"Migrated {migrated} image fields to Cloudinary.")
    if missing:
        print("Missing local files:")
        for item in missing:
            print(f"- {item}")


if __name__ == "__main__":
    migrate_images()
