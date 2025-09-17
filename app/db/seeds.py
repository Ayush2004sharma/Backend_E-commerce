import asyncio
import random
import uuid
from datetime import datetime, timedelta
from app.db.mongo import connect_to_mongo, db, close_mongo
from faker import Faker

fake = Faker()

NUM_PRODUCTS = 50
NUM_USERS = 8
EVENTS_PER_USER = 200

async def seed_products():
    products = []
    for i in range(NUM_PRODUCTS):
        pid = f"p{str(uuid.uuid4())[:8]}"
        products.append({
            "_id": pid,
            "name": f"{fake.word().capitalize()} {fake.word().capitalize()}",
            "category": random.choice(["electronics", "home", "beauty", "sports", "books"]),
            "brand": random.choice(["Acme", "Zenith", "BrandCo", "Alpha", "Beta"]),
            "price": round(random.uniform(5, 500), 2),
            "metadata": {"color": random.choice(["red", "green", "blue", "black"])},
            "created_at": datetime.utcnow()
        })
    await db["products"].insert_many(products)
    print(f"Inserted {len(products)} products")
    return [p["_id"] for p in products]

async def seed_users():
    users = []
    for i in range(NUM_USERS):
        uid = f"u{str(uuid.uuid4())[:8]}"
        users.append({
            "_id": uid,
            "email": f"user{i}@example.com",
            "password_hash": "seeded",  # placeholder
            "created_at": datetime.utcnow()
        })
    await db["users"].insert_many(users)
    print(f"Inserted {len(users)} users")
    return [u["_id"] for u in users]

async def seed_events(user_ids, product_ids):
    events = []
    now = datetime.utcnow()
    for uid in user_ids:
        for _ in range(EVENTS_PER_USER):
            pid = random.choice(product_ids)
            event_type = random.choices(
                ["view", "click", "add_to_cart", "purchase"],
                weights=[70, 20, 7, 3]
            )[0]
            ts = now - timedelta(days=random.randint(0, 30), seconds=random.randint(0, 86400))
            events.append({
                "_id": f"e{str(uuid.uuid4())[:10]}",
                "userId": uid,
                "sessionId": f"s{str(uuid.uuid4())[:8]}",
                "productId": pid,
                "eventType": event_type,
                "ts": ts
            })
    # Some guest events
    for _ in range(200):
        pid = random.choice(product_ids)
        events.append({
            "_id": f"e{str(uuid.uuid4())[:10]}",
            "userId": None,
            "sessionId": f"s{str(uuid.uuid4())[:8]}",
            "productId": pid,
            "eventType": random.choice(["view", "click"]),
            "ts": now - timedelta(days=random.randint(0, 30))
        })
    await db["events"].insert_many(events)
    print(f"Inserted {len(events)} events")

async def main():
    await connect_to_mongo()
    # cleanup for idempotent seed
    await db["products"].delete_many({})
    await db["users"].delete_many({})
    await db["events"].delete_many({})

    product_ids = await seed_products()
    user_ids = await seed_users()
    await seed_events(user_ids, product_ids)

    await close_mongo()
    print("Seeding complete")

if __name__ == "__main__":
    asyncio.run(main())
