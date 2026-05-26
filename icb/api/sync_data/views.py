import json
from fastapi.encoders import jsonable_encoder
from fastapi import Depends, HTTPException
from typing import Type, List,Optional
from sqlalchemy.sql import text

from main import app
from icb.core.db import db, engine
from icb.core.security import User, get_current_user_api_token
from icb.core.logger import logger
from icb.api.sync_data.schemas import FilterCondition
from icb.api.sync_setting.views import *
from icb.api.sync_data.log_sync import *
from sqlalchemy.dialects.postgresql import JSONB

import pandas as pd

@app.get("/api/v1/request-data")
async def request_data(
    table: str,
    filters: Optional[str] = None,
    current_user: User = Depends(get_current_user_api_token)
):
    """
    Retrieve data from a specified table for the authenticated user with optional filters.

    Args:
        table: The name of the table to query.
        filters: Optional JSON string of filter conditions (e.g., '[{"Column": "status", "operator": "IN", "value": ["active", "pending"]}]').
        current_user: Authenticated user.

    Returns:
        List of records from the specified table, filtered if applicable.
    """
    # Validate and parse filters
    filter_conditions = []
    query_params = {}
    if filters:
        try:
            filter_conditions = [FilterCondition(**f) for f in json.loads(filters)]
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=400, detail="Invalid filters format")

        # Validate operators and Columns
        allowed_operators = {"==", ">", "<", ">=", "<=", "LIKE", "BETWEEN", "IS NULL", "IS NOT NULL", "IN"}
        for idx, f in enumerate(filter_conditions):
            if f.operator.upper() not in allowed_operators:
                raise HTTPException(status_code=400, detail=f"Invalid operator: {f.operator}")
            # Validate Column name to prevent SQL injection
            if not f.field.isidentifier():
                raise HTTPException(status_code=400, detail=f"Invalid Column name: {f.field}")

    # Construct SQL query
    query = f"SELECT * FROM {table}"
    if filter_conditions:
        conditions = []
        for idx, f in enumerate(filter_conditions):
            operator = f.operator.upper()
            if operator in ["IS NULL", "IS NOT NULL"]:
                conditions.append(f"{f.field} {operator}")
            elif operator == "BETWEEN":
                query_params[f"param_{idx}_start"] = f.value[0]
                query_params[f"param_{idx}_end"] = f.value[1]
                conditions.append(f"{f.field} BETWEEN :param_{idx}_start AND :param_{idx}_end")
            elif operator == "IN":
                placeholders = [f":param_{idx}_{i}" for i in range(len(f.value))]
                query_params.update({f"param_{idx}_{i}": val for i, val in enumerate(f.value)})
                conditions.append(f"{f.field} IN ({', '.join(placeholders)})")
            else:
                query_params[f"param_{idx}"] = f.value
                if operator == "LIKE":
                    conditions.append(f"{f.field} {operator} :param_{idx}")
                elif operator == "==":
                    conditions.append(f"{f.field} = :param_{idx}")
                else:
                    conditions.append(f"{f.field} {operator} :param_{idx}")
        query += " WHERE " + " AND ".join(conditions)

    # Execute query with parameters
    try:
        result = pd.read_sql(text(query), engine, params=query_params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")

    # Replace NaT with None (for datetime fields) and NaN with None (for numeric/object fields)
    cleaned_df = result.astype(object).where(pd.notnull(result), None)
    records = cleaned_df.to_dict('records')
    logger.info(f"User {current_user.id} retrieved {len(records)} records from {table}")
    return jsonable_encoder(records)


@app.get("/api/v1/request-sync-config")
async def get_sync_config(
    table_name: Optional[str] = None,
    current_user: str = Depends(get_current_user_api_token)
):
    """
    Retrieve sync configuration (tables and filters) for all modules or specific tables.

    Args:
        table_name: Optional comma-separated list of table names to filter sync settings (e.g., 'TBL_CUSTOMER,TBL_SALE_ORDER').
        current_user: Authenticated user.

    Returns:
        Dictionary containing sync_tables and sync_filters based on sync settings and conditions.
    """
    try:
        # Query all sync settings
        query = TBL_SYNC_SETTING.__table__.select()
        table_names = [t.strip().upper() for t in (table_name.split(',') if table_name else [])] if table_name else None

        if table_names and not table_names[0]:  # Handle empty string case
            table_names = None

        if table_names:
            # Filter where model_name matches any table_name or any table_name is in sub_model_sync_include
            conditions = [
                or_(
                    TBL_SYNC_SETTING.model_name == t,
                    cast(TBL_SYNC_SETTING.sub_model_sync_include, JSONB).contains([t])
                )
                for t in table_names
            ]
            query = query.where(or_(*conditions))

        result = db.execute(query).fetchall()

        if not result:
            raise HTTPException(status_code=404, detail="No sync settings found")

        sync_tables = set()
        sync_filters = {}

        # Process each sync setting
        for row in result:
            setting = SyncSettingsSchema(
                module_name=row.module_name,
                model_name=row.model_name,
                enable_sync=row.enable_sync,
                sub_model_sync_include=','.join(row.sub_model_sync_include) if row.sub_model_sync_include else ''
            )

            # Add main model to sync_tables
            if setting.model_name:
                sync_tables.add(setting.model_name)

            # Add sub_models to sync_tables
            if setting.sub_model_sync_include:
                sync_tables.update(setting.sub_model_sync_include.split(','))

            # Query conditions for this module
            conditions_query = TBL_SYNC_CONDITION.__table__.select().where(TBL_SYNC_CONDITION.parent_id == row.id)
            conditions = db.execute(conditions_query).fetchall()

            if conditions:
                table_filters = []
                for cond_row in conditions:
                    if cond_row.condition_type == 'function':
                        continue
                    condition = SyncConditionSchema(
                        condition_type=cond_row.condition_type,
                        condition=cond_row.condition,
                        operator=cond_row.operator.lower(),
                        value=cond_row.value,
                        logic=cond_row.logic,
                        group_id=cond_row.group_id,
                        args=cond_row.args if cond_row.args else '{}'
                    )

                    operator = condition.operator.upper()

                    filter_cond = FilterCondition(
                        field=condition.condition,
                        operator=operator,
                        value=condition.value
                    )
                    table_filters.append(filter_cond.dict())

                # Assign filters to the model_name
                if setting.model_name and table_filters:
                    sync_filters[setting.model_name] = table_filters

        # Convert sync_tables to list
        sync_tables = list(sync_tables)

        response = {
            "sync_tables": sync_tables,
            "sync_filters": sync_filters
        }

        return response

    except HTTPException as e:
        raise e
    except Exception as e:
        # raise e
        raise HTTPException(status_code=500, detail=f"Database query failed: {str(e)}")