from enum import Enum
from main import app
from icb.core.crud_api import *
from .models import *
from icb.core.security import *
from icb.core.db_session import get_db
from fastapi import Depends, HTTPException, Query, status
import icb.core.lib as core_lib
from fastapi.responses import StreamingResponse
from datetime import datetime
import csv
import io
import logging
import time
import uuid
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class TableType(str, Enum):
    auth     = 'auth'
    unauth   = 'unauth'
    history  = 'history'
    deleted  = 'deleted'
    rejected = 'rejected'


def get_table_model(table_name: str, record_type: TableType = TableType.auth):
    resolved_table_name = table_name
    if record_type != TableType.auth and not table_name.endswith(f'_{record_type.value}'):
        resolved_table_name = f'{table_name}_{record_type.value}'

    module_obj = __import__("main")
    return getattr(module_obj, resolved_table_name.upper(), None)

@app.post("/api/v1/wb/export-file", tags=['Export File'])
async def export_file(
    table_name: str = None,
    record_type: TableType = TableType.auth,
    note: str = None,
    db: Session = Depends(get_db),
):
    try:
        if not table_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Table name is required"
            )

        audit = [
            're_status',
            're_created_by',
            're_created_at',
            're_deleted_at',
            're_deleted_by',
            'audit_date',
            'comment',
            'authorization',
            'branch_id',
            're_updated_by',
            're_updated_at',
        ]

        now      = datetime.now()
        filename = table_name[4:] + "_" + now.strftime("%Y%m%d%H%M%S") + ".csv"

        tableObj = get_table_model(table_name, record_type)
        if not tableObj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={'Not found': [f'Table "{table_name}" not found.']}
            )

        exportFile = TBL_EXPORT_FILE(
            id         = str(uuid.uuid4()),
            table_name = table_name,
            note       = note,
        )

        if hasattr(exportFile, 'company_id'):
            exportFile.company_id    = 'SYSTEM'
        if hasattr(exportFile, 're_status'):
            exportFile.re_status     = 'AUTH'
        if hasattr(exportFile, 're_created_by'):
            exportFile.re_created_by = 'SYSTEM'
        if hasattr(exportFile, 're_created_at'):
            exportFile.re_created_at = datetime.now()
        if hasattr(exportFile, 'audit_date'):
            exportFile.audit_date    = time.strftime('%Y-%m-%d %H:%M:%S')
        if hasattr(exportFile, 'branch_id'):
            exportFile.branch_id     = 'HQ'
        if hasattr(exportFile, 'flow_status'):
            exportFile.flow_status   = 'AUTH'
        if hasattr(exportFile, 'system_date'):
            exportFile.system_date   = time.strftime('%Y-%m-%d')

        db.add(exportFile)
        db.commit()

        queryObj = db.query(tableObj).all()

        file = io.StringIO()
        out  = csv.writer(file)

        columns = (
            queryObj[0].__table__.columns
            if queryObj
            else tableObj.__table__.columns
        )

        header = []
        for column in columns:
            if (column.name not in audit) or column.name == 'branch_id':
                header.append(column.name)

        out.writerow(header)

        for row in queryObj:
            out.writerow([getattr(row, col) for col in header])

        file.seek(0)

        return StreamingResponse(
            iter([file.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Export error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during export: " + str(e)
        )


@app.get("/api/v1/wb/table-list", tags=['Table List'])
async def table_list(
    current_user: User = Depends(get_current_active_user),
    table_type: TableType = TableType.auth,
    db: Session = Depends(get_db),
):
    try:
        result = db.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
        ))

        tableNames = []
        for row in result:
            tableName = row.table_name
            if table_type == TableType.auth:
                if not (
                    '_unauth'   in tableName or
                    '_history'  in tableName or
                    '_deleted'  in tableName or
                    '_rejected' in tableName
                ):
                    tableNames.append(tableName)
            elif tableName.endswith('_{0}'.format(table_type.value)):
                tableNames.append(tableName)

        return {
            "status":       True,
            "title":        "List Table",
            "message":      "List of Table",
            "module":       "tables",
            "data":         {"tables": tableNames},
            "total_record": len(tableNames),
            "page":         1,
            "size":         "all",
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Table list error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching table list: " + str(e)
        )


@app.get("/api/v1/wb/export-file", tags=['Export File'])
async def get_export_files(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(TBL_EXPORT_FILE)
        total = query.count()
        rows  = (
            query
            .order_by(TBL_EXPORT_FILE.re_created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )

        return {
            "ok":      True,
            "status":  200,
            "title":   "Export File",
            "message": "Data retrieved successfully",
            "data": {
                "lists": [
                    {
                        "id":            row.id,
                        "table_name":    row.table_name,
                        "note":          row.note,
                        "re_created_at": row.re_created_at,
                    }
                    for row in rows
                ],
                "meta_data": {
                    "total":        total,
                    "total_page":   (total + size - 1) // size if size else 1,
                    "current_page": page,
                    "size":         size,
                },
            },
            "error": {},
        }

    except Exception as e:
        logger.error(f"Get export files error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching export files: " + str(e)
        )
