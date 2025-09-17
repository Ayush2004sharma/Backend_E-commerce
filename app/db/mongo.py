# app/db/mongo.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.core.config import settings

client: Optional[AsyncIOMotorClient] = None
db = None

async def connect_to_mongo():
    global client, db
    if client:
        return
    client = AsyncIOMotorClient(settings.MONGO_URI)
    await client.admin.command("ping")
    db = client[settings.MONGO_DB]

    # create indexes useful for queries
    await db["events"].create_index([("userId", 1)])
    await db["events"].create_index([("productId", 1)])
    await db["events"].create_index([("ts", -1)])
    await db["users"].create_index([("email", 1)], unique=True)

    print(f"[MongoDB] ✅ Connected to {settings.MONGO_DB} at {settings.MONGO_URI}")


async def close_mongo():
    global client, db
    if client:
        client.close()
        client = None
        db = None
