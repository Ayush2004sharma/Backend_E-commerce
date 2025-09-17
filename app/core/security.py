# app/core/security.py
import jwt
import asyncio
import bcrypt
from datetime import datetime, timedelta
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional
from app.core.config import settings
from app.db import mongo  

security_scheme = HTTPBearer()

async def hash_password(password: str) -> str:
    rounds = settings.BCRYPT_ROUNDS
    hashed = await asyncio.to_thread(
        bcrypt.hashpw, password.encode("utf-8"), bcrypt.gensalt(rounds)
    )
    return hashed.decode()

async def verify_password(password: str, hashed: str) -> bool:
    return await asyncio.to_thread(bcrypt.checkpw, password.encode("utf-8"), hashed.encode("utf-8"))

def create_access_token(sub: str, minutes: Optional[int] = None) -> str:
    expire = datetime.utcnow() + timedelta(minutes=(minutes or settings.JWT_EXPIRES_MIN))
    payload = {"sub": sub, "exp": int(expire.timestamp())}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token invalid")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security_scheme)):
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = await mongo.db["users"].find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    # mask sensitive data
    user.pop("password_hash", None)
    return user
