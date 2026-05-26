import uuid, os 
from fastapi import File, Form, Query, UploadFile
from fastapi.responses import JSONResponse
from main import app
from sqlalchemy.orm import Session
from modules.job.models import TBL_JOB
from .models import *
from session import SessionLocal


UPLOAD_DIR = "uploads/cv"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def generateID():
    return str(uuid.uuid4())


@app.post("/api/v1/job-application", tags=["Job Application"])
async def submit_job_application(
    job_id       : str        = Query(..., description="ID of the job you are applying for"),
    full_name    : str        = Form(..., examples= [""]),
    email        : str        = Form(..., examples=[""]),
    phone_number: str         = Form(..., examples=[""]),
    gender       : str        = Form(..., examples=[""]),
    portfolio    : str        = Form(..., examples=[""]),
    linkedin_url: str         = Form("", examples=[""]),
    github_url   : str        = Form("", examples=[""]),
    other_url    : str        = Form("", examples=[""]),
    about_you    : str        = Form("", examples=[""]),
    upload_cv    : UploadFile = File(...),
):
    """
    Submit a job application.
    All fields are required except LinkedIn, GitHub, Other Link, and About You.
    """
    db: Session = SessionLocal()
    try:
        # Check job exists
        job = db.query(TBL_JOB).filter(TBL_JOB.id == job_id).first()
        if not job:
            return JSONResponse({"error": "Job not found"}, status_code=404)

        # Validate file size (max 20MB)
        content = await upload_cv.read()
        await upload_cv.seek(0)
        if len(content) > 20 * 1024 * 1024:
            return JSONResponse({"error": "File exceeds 20 MB limit"}, status_code=400)

        # Save file
        if not upload_cv.filename:
            return JSONResponse(
                {"error": "Invalid file upload"},
                status_code=400
            )
        file_ext = os.path.splitext(upload_cv.filename)[1].lower()
        allowed_ext = [".pdf", ".doc", ".docx"]
        if file_ext not in allowed_ext:
            return JSONResponse(
                {"error": "Only PDF or Word files are allowed"},
                status_code=400
            )
        file_name = f"{generateID()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(file_path, "wb") as f:
            f.write(content)

        # Determine version (increment for same parent_id and email)
        existing = db.query(TBL_JOB_APPLICATION)\
                     .filter(TBL_JOB_APPLICATION.parent_id == job_id)\
                     .filter(TBL_JOB_APPLICATION.email == email)\
                     .order_by(TBL_JOB_APPLICATION.re_version.desc())\
                     .first()
        version = existing.re_version + 1 if existing else 1

        # Save record
        record = TBL_JOB_APPLICATION(
            id           = generateID(),
            parent_id    = job_id,
            full_name    = full_name,
            email        = email,
            phone_number = phone_number,
            gender       = gender,
            portfolio    = portfolio,
            linkedin_url = linkedin_url,
            github_url   = github_url,
            other_url    = other_url,
            about_you    = about_you,
            upload_cv    = file_path,
            status       = "New",
            company_id   = "SYSTEM",
            re_version   = version
        )
        db.add(record)
        db.commit()

        return JSONResponse({
            "message"  : "Application submitted successfully",
            "job_title": job.title,
            "parent_id": job_id,
            "version"  : version
        })

    except Exception as e:
        db.rollback()
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        db.close()

"""
Get all job applications.
"""
@app.get("/api/v1/job-applications", tags=["Job Application"])
async def get_job_applications():
    db: Session = SessionLocal()
    try:
        applications = db.query(TBL_JOB_APPLICATION).all()
        return [
            {
                "id"          : application.id,
                "parent_id"   : application.parent_id,
                "full_name"   : application.full_name,
                "email"       : application.email,
                "phone_number": application.phone_number,
                "gender"      : application.gender,
                "portfolio"   : application.portfolio,
                "linkedin_url": application.linkedin_url,
                "github_url"  : application.github_url,
                "other_url"   : application.other_url,
                "about_you"   : application.about_you,
                "upload_cv"   : application.upload_cv,
                "status"      : application.status,
                "re_version"  : application.re_version
            }
            for application in applications
        ]
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        db.close()
