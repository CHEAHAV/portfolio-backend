import json
import time
from enum import Enum
from main import app
from icb.core.crud_api import *
from .models import *
from icb.core.security import *
from icb.core.db_session import get_db
from pathlib import Path
from fastapi import Depends, HTTPException, Query, status, UploadFile, File
import icb.core.lib as core_lib
import uuid
from datetime import datetime
import csv
import importlib
import logging
from urllib.parse import unquote, urlparse
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

HISTORY_TABLE_SUFFIXES = ('_unauth', '_history', '_deleted', '_rejected')
VERSION_TABLE_SUFFIXES = ('_history', '_deleted', '_rejected', '_unauth')

IMAGE_VALUE_FIELDS = {
    'image',
    'logo',
    'icon',
    'profile',
    'photo',
    'facebook',
    'youtube',
    'website',
    'facebook_icon',
    'linkedin_icon',
    'share_icon',
    'albums_memories',
}
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.bmp', '.pdf')


def is_image_value_field(column_name: str) -> bool:
    name = column_name.lower()
    return (
        name in IMAGE_VALUE_FIELDS
        or name.endswith(('_image', '_icon', '_logo', '_photo', '_profile'))
    )


def normalize_import_file_name(value):
    if not isinstance(value, str):
        return value

    value = value.strip()
    if not value or value.startswith('data:'):
        return value

    def normalize_one(raw_value: str) -> str:
        raw_value = raw_value.strip()
        if not raw_value:
            return raw_value

        parsed = urlparse(raw_value)
        path = parsed.path if parsed.scheme or parsed.netloc else raw_value
        path = unquote(path).replace('\\', '/').split('?')[0].split('#')[0]
        lower_path = path.lower()

        marker = '/static/images/'
        marker_index = lower_path.find(marker)
        if marker_index != -1:
            path = path[marker_index + len(marker):]

        file_name = Path(path).name
        if file_name.lower().endswith(IMAGE_EXTENSIONS):
            return file_name

        return raw_value

    if ',' in value:
        return ','.join(
            normalized
            for normalized in (normalize_one(item) for item in value.split(','))
            if normalized
        )

    return normalize_one(value)


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def get_existing_version(
    db: Session,
    table_name: str,
    tableObj,
    columns: dict,
    row: dict,
    table_columns_cache: dict,
):
    if table_name.endswith(HISTORY_TABLE_SUFFIXES) or 're_version' not in columns:
        return None

    primary_keys = [
        column.name
        for column in tableObj.__table__.primary_key.columns
        if column.name not in {'re_version', 're_deleted_at', 're_rejected_at'}
    ]
    if not primary_keys and 'id' in columns:
        primary_keys = ['id']

    max_version = None
    for suffix in VERSION_TABLE_SUFFIXES:
        version_table_name = f'{table_name}{suffix}'
        if version_table_name not in table_columns_cache:
            table_exists = db.execute(
                text("""
                    SELECT EXISTS (
                        SELECT 1
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                          AND table_name = :table_name
                    )
                """),
                {'table_name': version_table_name}
            ).scalar()
            if not table_exists:
                table_columns_cache[version_table_name] = None
                continue

            table_columns_cache[version_table_name] = {
                item.column_name
                for item in db.execute(
                    text("""
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_schema = 'public'
                          AND table_name = :table_name
                    """),
                    {'table_name': version_table_name}
                )
            }

        version_columns = table_columns_cache.get(version_table_name)
        if not version_columns or 're_version' not in version_columns:
            continue

        where_parts = []
        params = {}
        for key in primary_keys:
            if key in version_columns and key in row and row.get(key) not in ('', None):
                where_parts.append(f'{quote_identifier(key)} = :{key}')
                params[key] = row.get(key)

        if not where_parts:
            continue

        sql = (
            f'SELECT MAX(re_version) FROM {quote_identifier(version_table_name)} '
            f'WHERE {" AND ".join(where_parts)}'
        )
        version = db.execute(text(sql), params).scalar()
        if version is not None:
            max_version = max(int(max_version or 0), int(version))

    return max_version


class ImportType(Enum):
    add      = 'add'
    override = 'override'
    clear    = 'clear'

@app.post("/api/v1/wb/import-file", tags=['Import File'])
async def import_file(
    table_name: str = None,
    type: ImportType = ImportType.add,
    note: str = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    file: UploadFile = File(...)
):
    try:
        type_value       = type.value
        allow_extension  = ['csv']
        file_extension   = Path(file.filename).suffix.lower()[1:]

        if file_extension not in allow_extension:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid file extension. Only CSV files are allowed."
            )

        if not table_name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Table name is required"
            )

        if not type_value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Import Type is required"
            )

        record_id  = str(uuid.uuid4())
        importFile = TBL_IMPORT_FILE(
            id         = record_id,
            table_name = table_name,
            type       = type_value,
            note       = note,
        )

        if hasattr(importFile, 'company_id'):
            importFile.company_id    = getattr(current_user, 'company_id', 'SYSTEM')
        if hasattr(importFile, 're_status'):
            importFile.re_status     = 'AUTH'
        if hasattr(importFile, 're_created_by'):
            importFile.re_created_by = current_user.id
        if hasattr(importFile, 're_created_at'):
            importFile.re_created_at = datetime.now()
        if hasattr(importFile, 'audit_date'):
            importFile.audit_date    = time.strftime('%Y-%m-%d %H:%M:%S')
        if hasattr(importFile, 'branch_id'):
            importFile.branch_id     = getattr(
                current_user,
                "token_working_branch_id",
                getattr(current_user, "working_branch", "HQ")
            )
        if hasattr(importFile, 'flow_status'):
            importFile.flow_status   = 'AUTH'
        if hasattr(importFile, 'system_date'):
            importFile.system_date   = time.strftime('%Y-%m-%d')

        db.add(importFile)
        db.commit()

        tableObj = None
        model_class_name = table_name.upper()

        import sys
        for mod_name, mod in sys.modules.items():
            if hasattr(mod, model_class_name):
                candidate = getattr(mod, model_class_name)
                if hasattr(candidate, '__table__'):
                    tableObj = candidate
                    break

        if not tableObj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Table '{table_name}' was not found"
            )

        contents         = await file.read()
        decoded_contents = contents.decode(encoding='utf-8-sig')

        columns     = {}
        columnsData = tableObj.__table__.columns
        for column in columnsData:
            columnType           = str(column.type.compile(dialect=None)).split("(")[0]
            columns[column.name] = columnType.lower()

        csv_data = csv.DictReader(decoded_contents.splitlines())
        if not csv_data.fieldnames:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV file is empty or missing header row"
            )

        missing_columns = [f for f in csv_data.fieldnames if f not in columns]
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    'Not found': [
                        f"{model_class_name} has no attribute '{f}'"
                        for f in missing_columns
                    ]
                }
            )

        base_audit = {
            're_status'    : 'AUTH',
            're_created_by': current_user.id,
            're_created_at': datetime.now(),
            're_updated_by': current_user.id,
            're_updated_at': datetime.now(),
            're_deleted_at': None,
            'branch_id'    : getattr(
                current_user,
                "token_working_branch_id",
                getattr(current_user, "working_branch", "HQ")
            ),
        }

        if 're_version' in columns:
            base_audit['re_version'] = 0
        if 'audit_date' in columns:
            base_audit['audit_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
        if 'company_id' in columns:
            base_audit['company_id'] = getattr(current_user, 'company_id', 'SYSTEM')
        if 'flow_status' in columns:
            base_audit['flow_status'] = 'AUTH'
        if 'system_date' in columns:
            base_audit['system_date'] = time.strftime('%Y-%m-%d')

        overrideColumnTypes = ['datetime', 'json', 'timestamp', 'date']
        integer_types       = ('integer', 'biginteger', 'smallinteger', 'int', 'bigint', 'smallint')
        float_types         = ('float', 'numeric', 'decimal', 'double_precision', 'real')
        listData            = []
        table_columns_cache = {}

        for row in csv_data:
            dataDict = dict(row)
            audit = base_audit.copy()
            imported_re_version = None

            if 're_version' in row and row['re_version']:
                imported_re_version = row['re_version']
                audit['re_version'] = row['re_version']
                dataDict.pop('re_version', None)

            if 'branch_id' in row and row['branch_id']:
                audit['branch_id'] = row['branch_id']
                dataDict.pop('branch_id', None)

            dataDict.update(audit)

            if 're_version' in columns and not table_name.endswith(HISTORY_TABLE_SUFFIXES):
                try:
                    imported_version = int(imported_re_version or dataDict.get('re_version') or 0)
                except (ValueError, TypeError):
                    imported_version = 0

                existing_version = get_existing_version(
                    db,
                    table_name,
                    tableObj,
                    columns,
                    dataDict,
                    table_columns_cache,
                )
                if existing_version is not None:
                    dataDict['re_version'] = max(imported_version, int(existing_version) + 1)
                else:
                    dataDict['re_version'] = imported_version

            for col_name in list(dataDict.keys()):
                if col_name not in columns:
                    continue

                col_type = columns[col_name]
                val      = dataDict[col_name]

                if col_type == 'boolean':
                    if isinstance(val, bool):
                        pass
                    else:
                        dataDict[col_name] = (
                            False if str(val).strip().lower()
                            in ['0', 'false', 'f', 'no', ''] else True
                        )

                elif col_type == 'time':
                    dataDict[col_name] = None if val == '' else val

                elif col_type in overrideColumnTypes:
                    if val == '' or val is None or str(val).strip().lower() in ['nan', 'nat']:
                        dataDict[col_name] = None
                    elif col_type == 'json':
                        try:
                            dataDict[col_name] = json.loads(val) if val else None
                        except (json.JSONDecodeError, TypeError):
                            dataDict[col_name] = None

                elif col_type in integer_types:
                    if val in ('', None):
                        dataDict[col_name] = None
                    else:
                        try:
                            dataDict[col_name] = int(val)
                        except (ValueError, TypeError):
                            dataDict[col_name] = None

                elif col_type in float_types:
                    if val in ('', None):
                        dataDict[col_name] = None
                    else:
                        try:
                            dataDict[col_name] = float(val)
                        except (ValueError, TypeError):
                            dataDict[col_name] = None

                elif col_type in ('varchar', 'text', 'character varying'):
                    if val == '':
                        dataDict[col_name] = None
                    elif is_image_value_field(col_name):
                        dataDict[col_name] = normalize_import_file_name(val)

            listData.append(dataDict)

        # Validate all keys exist on the model
        if listData:
            for key in listData[0]:
                if not hasattr(tableObj, key):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail={'Not found': [f"{model_class_name} has no attribute '{key}'"]}
                    )

        if type_value == 'clear':
            db.execute(text(f'DELETE FROM "{table_name}"'))
            db.commit()

        elif type_value == 'override':
            for delete in listData:
                current_id = delete.get('id', '')
                if current_id:
                    db.execute(text(f"DELETE FROM \"{table_name}\" WHERE id = '{current_id}'"))
            db.commit()

        for row in listData:
            dataEntry = tableObj(**row)
            db.add(dataEntry)
        db.commit()

        return {
            'ok':      True,
            'message': "Records imported successfully",
            'total':   len(listData),
        }

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"Import error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during import: " + str(e)
        )

@app.get("/api/v1/wb/import-file", tags=['Import File'])
async def get_import_files(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(TBL_IMPORT_FILE)
        total = query.count()
        rows  = (
            query
            .order_by(TBL_IMPORT_FILE.re_created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )

        return {
            "ok":      True,
            "status":  200,
            "title":   "Import File",
            "message": "Data retrieved successfully",
            "data": {
                "lists": [
                    {
                        "id":            row.id,
                        "table_name":    row.table_name,
                        "type":          row.type,
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
        logger.error(f"Get import files error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while fetching import files: " + str(e)
        )