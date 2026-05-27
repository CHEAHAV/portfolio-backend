import os
import uuid
from fastapi.responses import JSONResponse
from modules.job.models import TBL_JOB
from modules.job_application.models import TBL_JOB_APPLICATION
from modules.location_join import prefixed_id_join
from modules.province.models import TBL_PROVINCE
from icb.core.db_session import SessionLocal, get_db
from main import website
from fastapi import Depends, File, Form, HTTPException, Path, Query, UploadFile
from sqlalchemy.orm import Session
import math

@website.get("/job-list", tags=["Job"])
async def get_job(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db)
):
    base_query = (
        db.query(TBL_JOB, TBL_PROVINCE)
        .outerjoin(TBL_PROVINCE, prefixed_id_join(TBL_PROVINCE.id, TBL_JOB.province_id, "PRO")))

    total   = base_query.count()
    results = base_query.order_by(TBL_JOB.title\
                        .asc())\
                        .offset((page - 1) * size)\
                        .limit(size)\
                        .all()
    total_pages = math.ceil(total / size) if size else 1

    data_list = [{
        'id'                : job.id,
        'title'             : job.title,
        'department_id'     : job.department_id,
        'province_name'     : province_name.name if province_name else None,
        'employment_type'   : job.employment_type,
        'position_available': job.position_available,
        'salary_range'      : job.salary_range,
        'urgent_flag'       : job.urgent_flag,
        'order'             : job.order,
        'active'            : job.active,
    } for job, province_name in results ]
    
    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'Job',
        'message': 'Data retrieved successfully',
        'data'   : {
            'lists'    : data_list,
            'meta_data': {
                'total'       : total,
                'total_page'  : total_pages,
                'current_page': page,
                'size'        : size,
            }
        },
        'error': {}
    }


@website.get("/job-detail/{id}", tags=["Job"])
async def get_job_detail(
    id: str,
    db: Session = Depends(get_db)
):
    try: 
        job = (db.query(TBL_JOB,TBL_PROVINCE)\
                 .outerjoin(TBL_PROVINCE, prefixed_id_join(TBL_PROVINCE.id, TBL_JOB.province_id, "PRO"))\
                 .filter(TBL_JOB.id == id)\
                 .first())
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        job, province_name = job

        job_data = {
            'id'                : job.id,
            'title'             : job.title,
            'department_id'     : job.department_id,
            'province_id'       : job.province_id,
            'province_name'     : province_name.name if province_name else None,
            'district_id'       : job.district_id,
            'commune_id'        : job.commune_id,
            'village_id'        : job.village_id,
            'employment_type'   : job.employment_type,
            'position_available': job.position_available,
            'salary_range'      : job.salary_range,
            'work_start_time'   : job.work_start_time,
            'work_end_time'     : job.work_end_time,
            'urgent_flag'       : job.urgent_flag,
            'role'              : job.role,
            'responsibilities'  : job.responsibilities,
            'qualifications'    : job.qualifications,
            'status'            : job.status,
            'order'             : job.order,
            'active'            : job.active,
        }

        return {
            'ok'     : True,
            'status' : 200,
            'title'  : 'Job Detail',
            'message': 'Job detail retrieved successfully',
            'data'   : job_data,
            'error'  : {}
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
UPLOAD_DIR = "uploads/cv"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def generateID():
    return str(uuid.uuid4())


@website.post("/job-application/{job_id}", tags=["Job"])
async def submit_job_application(
    job_id      : str = Path(..., description="ID of the job you are applying for"),
    full_name   : str = Form(..., examples=[""]),
    email       : str = Form(..., examples=[""]),
    phone_number: str = Form(..., examples=[""]),
    gender      : str = Form(..., examples=[""]),
    portfolio   : str = Form(..., examples=[""]),
    linkedin_url: str = Form("",examples=[""]),
    github_url  : str = Form("", examples=[""]),
    other_url   : str = Form("", examples=[""]),
    about_you   : str = Form("", examples=[""]),
    upload_cv   : UploadFile = File(...),
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

        # Validate file upload
        if not upload_cv.filename: 
            return JSONResponse(
                {"error": "Invalid file upload"},
                status_code=400
            )

        # Read file content
        content = await upload_cv.read()
        
        # Validate file size (max 20MB)
        if len(content) > 20 * 1024 * 1024:
            return JSONResponse({"error": "File exceeds 20 MB limit"}, status_code=400)

        # Validate file extension
        file_ext = os.path.splitext(upload_cv.filename)[1].lower()
        allowed_ext = [".pdf", ".doc", ".docx"]
        if file_ext not in allowed_ext: 
            return JSONResponse(
                {"error": "Only PDF or Word files are allowed"},
                status_code=400
            )

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
        print(f"Error: {str(e)}")
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        db.close()


@website.put("/job-application/{id}", tags=["Job"])
async def update_job_application(
    id          : str = Path(..., description="ID of the job application"),
    full_name   : str = Form(..., examples=[""]),
    email       : str = Form(..., examples=[""]),
    phone_number: str = Form(..., examples=[""]),
    gender      : str = Form(..., examples=[""]),
    portfolio   : str = Form(..., examples=[""]),
    linkedin_url: str = Form("", examples=[""]),
    github_url  : str = Form("", examples=[""]),
    other_url   : str = Form("", examples=[""]),
    about_you   : str = Form("", examples=[""]),
    upload_cv   : UploadFile | None = File(None),
    db          : Session = Depends(get_db),
):
    record = db.query(TBL_JOB_APPLICATION).filter(TBL_JOB_APPLICATION.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Job application not found")

    record.full_name = full_name
    record.email = email
    record.phone_number = phone_number
    record.gender = gender
    record.portfolio = portfolio
    record.linkedin_url = linkedin_url
    record.github_url = github_url
    record.other_url = other_url
    record.about_you = about_you

    if upload_cv and upload_cv.filename:
        content = await upload_cv.read()
        if len(content) > 20 * 1024 * 1024:
            return JSONResponse({"error": "File exceeds 20 MB limit"}, status_code=400)

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
        record.upload_cv = file_path

    db.commit()
    db.refresh(record)

    return {
        "ok"     : True,
        "status" : 200,
        "title"  : "Job Application",
        "message": "Data updated successfully",
        "data"   : {
            "id"          : record.id,
            "parent_id"   : record.parent_id,
            "full_name"   : record.full_name,
            "email"       : record.email,
            "phone_number": record.phone_number,
            "gender"      : record.gender,
            "portfolio"   : record.portfolio,
            "linkedin_url": record.linkedin_url,
            "github_url"  : record.github_url,
            "other_url"   : record.other_url,
            "about_you"   : record.about_you,
            "upload_cv"   : record.upload_cv,
            "status"      : record.status,
        },
        "error": {},
    }
