import secrets
from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from icb.api.user.models import TBL_USER
from icb.core.db import db
from icb.config import settings
from icb.lib.aes_encryption import encrypt
from icb.core.security import User, get_current_active_user, get_current_user_api_token, get_password_hash, verify_password
from main import app
from datetime import datetime, timedelta, timezone
import uuid

from .models import TBL_API_TOKEN
from .schemas import ApiTokenSchema


@app.post("/api/v1/api-token/generate", tags=["API Token"])
async def generate_api_token(
    body: ApiTokenSchema,
    current_user: User = Depends(get_current_active_user),
):
    try:
        """
        Generate a new API token.
        """
        token_prefix = 'sds'
        # Generate a unique token
        raw_token = secrets.token_urlsafe(32)
        token = f"{token_prefix}-{raw_token}"

        hashed_token = get_password_hash(token)
        secret_key = settings.AES_SECRET_KEY
        backup_key = encrypt(token, secret_key)
        origins = ','.join(body.origins) if body.origins else ''

        db.add(
            TBL_API_TOKEN(
                id=str(uuid.uuid4()),
                name=body.name,
                token_hash=hashed_token,
                user_id=current_user.id,
                scope="full_access",
                origins=origins,
                backup_key=backup_key,
                re_created_at=datetime.now(),
                re_created_by=current_user.id,
                expires_at=body.expires_at,
                revoked=False
            )
        )
        db.commit()

        # Return the raw token to the user (hashed token is stored in the database)
        return {"api_token": token, "message": "API token created successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/api-token/verify", tags=["API Token"])
async def validate_api_token(api_token: str):
    """
    Validate an API token.
    """
    # Fetch the token from the database
    token_entry = db.query(TBL_API_TOKEN).filter_by(revoked=False).all()

    for token in token_entry:
        if verify_password(api_token, token.token_hash):
            # Check if the token is expired
            if token.last_used_at and token.last_used_at + timedelta(days=30) < datetime.now():
                return {"valid": False, "message": "Token is invalid"}

            # Update the last used timestamp
            token.last_used_at = datetime.now()
            db.commit()
            return {"valid": True, "message": "Token is valid"}

    # If no matching token is found
    return {"valid": False, "message": "Token is invalid"}


@app.delete("/api/v1/api-token/revoke", tags=["API Token"])
async def revoke_api_token(
    id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Revoke an API token.
    """
    try:
        # Fetch all non-revoked tokens for the current user
        token = db.query(TBL_API_TOKEN).filter_by(
            revoked=False,
            user_id=current_user.id,
            id=id
        ).first()
        
        if not token:
            raise HTTPException(status_code=404, detail="Token not found")
        
        token.revoked = True
        token.re_deleted_at = datetime.now()
        token.re_deleted_by = current_user.id
        db.commit()

        return {"message": "Token revoked successfully."}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/api-token/test", tags=["API Token"])
async def test_api_token(
    current_user: User = Depends(get_current_user_api_token)
):
    """
    Test the API token.
    """
    try:
        user_info = db.query(TBL_USER).filter_by(
            id=current_user.id
        ).first()

        return {
            "message": "Token is valid",
            "user_info": {
                "id": user_info.id,
                "email": user_info.email,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/api-token", tags=["API Token"])
async def get_api_tokens(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all API tokens for the current user.
    """
    try:
        tokens = db.query(TBL_API_TOKEN).filter_by(
            revoked=False,
            user_id=current_user.id
        ).all()

        data = {
            "lists": [
                {
                    "id": token.id,
                    "name": token.name,
                    "token_hash": "*" * 8 + token.token_hash[-4:] if token.token_hash else None,
                    "re_created_at": token.re_created_at,
                    "expires_at": token.expires_at,
                    "origins": token.origins,
                    "last_used_at": token.last_used_at,
                }
                for token in tokens
            ]
        }

        return JSONResponse({
            'ok': True,
            'status': 200,
            'title': "API Token",
            "message": 'Data retrieved successfully',
            "error": {},
            'data': jsonable_encoder(data),
            "request_id": app.state.request_id
        }, status_code=200)
    except Exception as error:
        return JSONResponse({
            'ok': False,
            'status': 500,
            'title': 'Error',
            "message": str(error),
            "error": {"detail": str(error)},
            'data': [],
            "request_id": app.state.request_id
        }, status_code=500)
