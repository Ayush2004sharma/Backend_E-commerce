# app/services/rec_service.py
import time
from app.ml.artifact_store import read_json
from app.db import mongo
from datetime import datetime, timedelta

# simple in-memory TTL cache for artifacts
_ART_CACHE = {}
_ART_CACHE_TTL = 60 * 60  # 1 hour

def _load_artifact(name):
    now = time.time()
    entry = _ART_CACHE.get(name)
    if entry and now - entry["ts"] < _ART_CACHE_TTL:
        return entry["data"]
    data = read_json(name)
    _ART_CACHE[name] = {"ts": now, "data": data}
    return data

async def _get_last_viewed(userId: str, limit: int = 5):
    q = {"userId": userId, "eventType": {"$in": ["view","click","add_to_cart","purchase"]}}
    count = await mongo.db["events"].count_documents(q)
    print(f"[DEBUG] Found {count} events for user {userId} with query {q}")

    cursor = mongo.db["events"].find(q).sort("ts", -1).limit(limit)

    items = []
    async for doc in cursor:
        print(f"[DEBUG] Event doc: {doc}")  # 👀 see what is actually stored
        items.append(doc.get("productId"))
    return items


async def recommend_for_user(userId: str, n: int = 10):
    # load artifacts
    pop = _load_artifact("popularity.json") or []
    sim = _load_artifact("similarity.json") or {}
    # personalization: use last viewed items and aggregate similar items
    last_viewed = await _get_last_viewed(userId, limit=5)
    scores = {}
    reasons = {}
    print(f"[DEBUG] Last viewed items for user {userId}: {last_viewed}")
    for lv in last_viewed:
        print(f"[DEBUG] Similar items for {lv}: {sim.get(lv, [])[:5]}")  # show top 5 similar
        neighbors = sim.get(lv, [])[:20]
        for nb in neighbors:
            pid = nb["productId"]
            scores[pid] = scores.get(pid, 0.0) + nb["score"]
            reasons.setdefault(pid, []).append(f"Because you viewed {lv}")
    # fallback: if no personalization or not enough items, fill with popularity
    if not scores:
        # return top popularity
        recommendations = []
        for p in pop[:n]:
            recommendations.append({
                "productId": p["productId"],
                "score": p["score"],
                "why": "Popular item"
            })
        return recommendations
    # convert scores to sorted list, avoid items user already interacted heavily with
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    recs = []
    for pid, score in ranked[:n]:
        why = reasons.get(pid, ["Similar items"])[0]
        recs.append({"productId": pid, "score": float(score), "why": why})
    # fill with popularity if < n
    existing = {r["productId"] for r in recs}
    if len(recs) < n:
        for p in pop:
            if p["productId"] not in existing:
                recs.append({"productId": p["productId"], "score": p["score"], "why": "Popular item"})
            if len(recs) >= n:
                break
    return recs

async def similar_items(productId: str, n: int = 10):
    sim = _load_artifact("similarity.json") or {}
    neighbours = sim.get(productId, [])[:n]
    return neighbours
