import math
import os
import logging

from main import app
from icb.core.crud_api import *
from .models import *
from icb.core.security import *
from icb.core.db_session import get_db
from pathlib import Path
from fastapi import Depends, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import icb.core.lib as core_lib
import uuid
from datetime import datetime
import time
from icb.lib.render_api import response_msg
from icb.lib.upload_lib import upload_image_file
from icb.lib.s3_lib import delete_file_from_aws
import zipfile
import io
from urllib.parse import quote

logger = logging.getLogger(__name__)


def unique_file_name_for_folder(folder: str, file_name: str, is_private: bool = False) -> str:
    source_name = Path(file_name).name
    file_path = (
        BASE_DIR + '/uploads/%s%s'
        if is_private
        else BASE_DIR + '/static/images/%s%s'
    ) % ('%s/' % folder if folder else '', source_name)

    if not os.path.exists(file_path):
        return source_name

    suffix = Path(source_name).suffix.lower()
    stem = Path(source_name).stem or 'upload'
    return f"{stem}-{uuid.uuid4().hex}{suffix}"

# Custom route for import file
@app.post("/api/v1/wb/upload-file", tags=['Upload File'])
async def upload_files(
    folder: str = Form(default=''),
    current_user  : User       = Depends(get_current_active_user),
    db            : Session    = Depends(get_db),
    file          : UploadFile = File(...),
    module        : str        = Form(default=''),
    module_id     : str        = Form(default=''),
    is_private    : bool       = Form(False),
    keep_file_name: bool       = Form(False),
):
    try:
        # User permission
        
        allow_extension = ['pdf','jpeg','png','jpg','gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip']
        file_extension  = Path(file.filename).suffix.lower()[1:]
        original_name   = file.filename
        file_name       = '%s.%s'%(uuid.uuid4(), file_extension)
        response_file_name = file_name
        
        # Validate file extension
        if file_extension not in allow_extension:
            msg="Invalid file extension. Only files with extension %s are allowed."%(', '.join(allow_extension))
            return response_msg('File Upload', msg, 400, False)
    

        # check the content type (MIME type)
        content_type = file.content_type

        if content_type not in [
            'application/pdf', 
            "image/jpeg", 
            "image/png", 
            "image/gif", 
            "image/jpg", # jpg
            "application/vnd.ms-excel",# xls
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",# xlsx
            "application/msword", # doc
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document", # docx
            "application/vnd.ms-powerpoint", # ppt
            "application/vnd.openxmlformats-officedocument.presentationml.presentation", # pptx
            "application/x-zip-compressed",
            "application/zip"
        ]:
            
            return response_msg('File Upload', "Invalid file type", 400, False)
                       
        module_id  = module_id if module_id else None
        module     = module if module else None
        is_private = is_private if is_private else False
        
        if file_extension == 'zip':
            # Convert the file content into a BytesIO object
            file_content = await file.read()
            file_bytes   = io.BytesIO(file_content)

            # Process the ZIP file using the BytesIO object 
            with zipfile.ZipFile(file_bytes, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    original_name = os.path.basename(file_info.filename)
                    
                    if not original_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) or '__macosx' in file_info.filename.lower():
                        continue

                    file_extension = Path(original_name).suffix.lower()[1:]
                    file_name      = '%s.%s'%(uuid.uuid4(), file_extension)
                    
                     # Read the extracted file content
                    with zip_ref.open(file_info) as extracted_file:
                        image_content   = extracted_file.read()
                        image_file      = io.BytesIO(image_content)
                        image_file.name = file_name

                    # Create new record in table file_import
                    id   = str(uuid.uuid4())
                    fobj = TBL_FILE_UPLOAD(
                        id            = id,
                        module        = module,
                        module_id     = None,
                        file_name     = file_name,
                        original_name = original_name,
                        folder        = folder,
                        operation     = 'ADD',
                        re_status     = 'AUTH',
                        re_created_by = current_user.id,
                        re_created_at = datetime.now(),
                        company_id    = "SYSTEM",
                        is_private    = is_private
                    )

                    upload_image_file(image_file, folder, original_name, is_private=is_private, args={}, file_extension='zip')

                    db.add(fobj)

            db.commit() 
        else :  
             # Get the file size (in bytes)
            file.file.seek(0, 2)
            file_size = file.file.tell()

            # move the cursor back to the beginning
            await file.seek(0)

            # more than 50 MB
            if file_size > 50 * 1024 * 1024:
                return response_msg('File Upload', "File too large", 400, False)

            # Create new record in table file_import
            id   = str(uuid.uuid4())
            stored_file_name = unique_file_name_for_folder(
                folder,
                original_name if keep_file_name else file_name,
                is_private=is_private,
            )
            response_file_name = stored_file_name

            fobj = TBL_FILE_UPLOAD(
                id            = id,
                module        = module,
                module_id     = module_id,
                file_name     = stored_file_name,
                original_name = original_name,
                folder        = folder,
                operation     = 'ADD',
                re_status     = 'AUTH',
                re_created_by = current_user.id,
                re_created_at = datetime.now(),
                company_id    = "SYSTEM",
                is_private    = is_private
            )
            
            upload_image_file(file, folder, stored_file_name, is_private=is_private)
                        
            db.add(fobj)
            db.commit()
            
        # Return record with success message
        return response_msg('File Upload', "File is uploaded successfully", 200, True, 
                            data={
                                "file_name" : response_file_name,
                                "folder"    : folder,
                                "module"    : module,
                                "module_id" : module_id,
                                "is_private": is_private
                            })
        
    except Exception as e:
        logger.error(e)
        raise e
    
@app.delete("/api/v1/wb/delete-upload-file", tags=['Upload File'])
async def delete_upload_files(
    id: str = '',
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    obj = db.query(TBL_FILE_UPLOAD).filter(TBL_FILE_UPLOAD.id == id).first()
    if obj:
        obj.operation = 'DEL'
        obj.re_deleted_at = datetime.now()
        obj.re_deleted_by = current_user.id
        db.add(obj)
        db.commit()
        
        file_path = (
            BASE_DIR + '/uploads/%s%s'
            if obj.is_private
            else BASE_DIR + '/static/images/%s%s'
        ) % ('%s/' % obj.folder if obj.folder else '', obj.file_name)
        
        if os.path.exists(file_path):
            os.remove(file_path)
        
        if os.getenv('FILE_STORAGE') == 'S3':
            delete_file_from_aws('%s%s'%('%s/'%obj.folder if obj.folder else '', obj.file_name))
        
        return response_msg('File Upload', "File is deleted successfully", 200, True)
        
    return response_msg('File Upload', "File is not found", 400, False)

@app.get("/api/v1/wb/list-upload-file", tags=['Upload File'])
async def list_upload_files(
    lang        : str     = 'kh',
    current_user: User    = Depends(get_current_active_user),
    db          : Session = Depends(get_db),
    page        : int     = Query(default=1,  ge=1),
    size        : int     = Query(default=10, ge=1)
):
    obj =   db.query(
                TBL_FILE_UPLOAD.id,
                TBL_FILE_UPLOAD.file_name,
                TBL_FILE_UPLOAD.original_name,
                TBL_FILE_UPLOAD.module,
                TBL_FILE_UPLOAD.module_id,
                TBL_FILE_UPLOAD.folder,
                TBL_FILE_UPLOAD.re_created_by,
                TBL_FILE_UPLOAD.re_created_at,
            ).\
            filter(TBL_FILE_UPLOAD.operation == "ADD").\
            order_by(TBL_FILE_UPLOAD.re_created_at.desc())
    
    page    = page - 1
    obj     = obj.limit(size).offset(page*size)
    total   = obj.count()
    t_page  = math.ceil(total/size)
    
    return {
        'ok'     : True,
        'status' : 200,
        'title'  : 'File Upload',
        "message": core_lib.getLang('data_retrieved_successful', lang=lang),
        "error"  : {},
        'data'   : {
          'file_upload': jsonable_encoder(obj.all()),
          "meta_data"  : {
            'total'       : total,
            'total_page'  : t_page,
            'current_page': page+1,
            'size'        : size
          },
        },
        "redirect_url": "",
        "request_id"  : app.state.request_id
    }

@app.get("/api/v1/wb/get-uploaded-file", tags=['Upload File'])
async def get_uploaded_files(
    lang        : str = 'kh',
    current_user: User = Depends(get_current_active_user),
    db          : Session = Depends(get_db),
    module      : str = None,
    module_id   : str = None,
    file_name   : str = ''
    ): 
   
    obj = db.query(
                TBL_FILE_UPLOAD.id,
                TBL_FILE_UPLOAD.file_name,
                TBL_FILE_UPLOAD.original_name,
                TBL_FILE_UPLOAD.module,
                TBL_FILE_UPLOAD.module_id,
                TBL_FILE_UPLOAD.folder,
                TBL_FILE_UPLOAD.is_private
            ).\
            filter(TBL_FILE_UPLOAD.operation == "ADD").\
            filter(TBL_FILE_UPLOAD.module == module).\
            filter(TBL_FILE_UPLOAD.module_id == module_id).\
            filter(TBL_FILE_UPLOAD.file_name == file_name).\
            first()
    if obj: 
        filename = obj.file_name
        headers  = {}
          # Determine media type based on file extension
        if filename.endswith(".pdf"): 
            media_type = "application/pdf"
            headers    = {"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"}
        elif filename.endswith((".jpg", ".jpeg", ".png")): 
            media_type = "image/jpeg"
        else: 
            media_type = "application/octet-stream"  # Default for unknown file types

        if obj.is_private: 
            file_path = BASE_DIR + '/uploads/%s%s'%( '%s/'%obj.folder if obj.folder else '', obj.file_name)
            if os.path.exists(file_path): 
                return FileResponse(file_path, media_type=media_type, headers= headers)
            else: 
                return response_msg('File Upload', "File is not found", 400, False)
        else: 
            file_path = BASE_DIR + '/static/images/%s%s'%( '%s/'%obj.folder if obj.folder else '', obj.file_name)
              # print(file_path)
            if os.path.exists(file_path): 
                return FileResponse(file_path, media_type=media_type)
            else: 
                return response_msg('File Upload', "File is not found", 400, False)
    else: 
        return response_msg('File Upload', "File is not found", 400, False)
    
    
# https://www.slingacademy.com/article/fastapi-how-to-upload-and-validate-files/



# Custom route for import file
@app.post("/api/v1/wb/upload-image-file", tags=['Upload File'])
async def upload_image_files(
    folder: str = '',
    current_user: User = Depends(get_current_active_user),
    db          : Session = Depends(get_db),
    file        : UploadFile = File(...),
): 
    try:
        allow_extension = ['jpeg','png','jpg','gif']
        file_extension  = Path(file.filename).suffix.lower()[1:]
        file_name       = unique_file_name_for_folder(folder, file.filename)
        
        # Validate file extension
        if file_extension not in allow_extension:
            msg="Invalid file extension. Only files with extension %s are allowed."%(', '.join(allow_extension))
            return response_msg('Image Upload', msg, 400, False)
            
        
        # Get the file size (in bytes)
        file.file.seek(0, 2)
        file_size = file.file.tell()

        # move the cursor back to the beginning
        await file.seek(0)

        if file_size > 20 * 1024 * 1024:
            # more than 20 MB
            # raise HTTPException(status_code=400, detail="File too large")
            return response_msg('Image Upload', "File too large", 400, False)

        # check the content type (MIME type)
        content_type = file.content_type
        if content_type not in ["image/jpeg", "image/png", "image/gif", "image/jpg"]:
            # raise HTTPException(status_code=400, detail="Invalid file type")  
            return response_msg('Image Upload', "Invalid file type", 400, False)
                       
    
        # Create new record in table file_import
        id = str(uuid.uuid4())
        fobj = TBL_FILE_UPLOAD(
            id            = id,
            file_name     = file_name,
            folder        = folder,
            operation     = 'ADD',
            re_status     = 'AUTH',
            re_created_by = current_user.id,
            re_created_at = datetime.now(),
            company_id    = "SYSTEM", 
        )
        
        upload_image_file(file, folder, file_name, {'ContentType':content_type})
        
        db.add(fobj)
        db.commit()
            
        # Return record with success message
        return response_msg(
            'Image Upload',
            "File is uploaded successfully",
            200,
            True,
            data={"file_name": file_name, "folder": folder},
        )
        
    except Exception as e:
        raise e
