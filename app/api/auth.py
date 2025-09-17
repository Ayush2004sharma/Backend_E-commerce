from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.auth import SignupIn, LoginIn, TokenOut, UserOut
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.db import mongo
from datetime import datetime
import uuid

router = APIRouter()

# Signup endpoint
@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupIn):
    if mongo.db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    existing = await mongo.db["users"].find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = f"u{str(uuid.uuid4())[:8]}"
    password_hash = await hash_password(payload.password)

    user = {
        "_id": user_id,
        "name": payload.name,
        "email": payload.email,
        "password_hash": password_hash,
        "created_at": datetime.utcnow(),
    }

    await mongo.db["users"].insert_one(user)

    return {k: user[k] for k in ("_id", "name", "email", "created_at")}


# Login endpoint
@router.post("/login", response_model=TokenOut)
async def login(payload: LoginIn):
    if mongo.db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    user = await mongo.db["users"].find_one({"email": payload.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    valid = await verify_password(payload.password, user["password_hash"])
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user["_id"])
    return {"accessToken": token, "tokenType": "bearer"}


# Get current user
@router.get("/me", response_model=UserOut)
async def me(user=Depends(get_current_user)):
    return {
        "_id": user["_id"],
        "name": user.get("name"),
        "email": user["email"],
        "created_at": user["created_at"],
    }


# Update current user
@router.put("/me", response_model=UserOut)
async def update_me(payload: SignupIn, user=Depends(get_current_user)):
    if mongo.db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    update_data = {}

    # Update name if provided
    if hasattr(payload, "name") and payload.name:
        update_data["name"] = payload.name

    # Update email if provided and changed
    if hasattr(payload, "email") and payload.email and payload.email != user["email"]:
        existing = await mongo.db["users"].find_one({"email": payload.email})
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")
        update_data["email"] = payload.email

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    await mongo.db["users"].update_one({"_id": user["_id"]}, {"$set": update_data})

    updated_user = await mongo.db["users"].find_one({"_id": user["_id"]})
    return {k: updated_user[k] for k in ("_id", "name", "email", "created_at")}


# Delete current user
@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(user=Depends(get_current_user)):
    if mongo.db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")

    result = await mongo.db["users"].delete_one({"_id": user["_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return None
