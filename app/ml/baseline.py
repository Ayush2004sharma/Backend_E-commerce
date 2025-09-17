# app/ml/baseline.py
import pandas as pd
import numpy as np
from collections import defaultdict

def popularity_from_events(events_df: pd.DataFrame) -> list:
    """
    Compute popularity scores by counting weighted events.
    weights: view=1, click=2, add_to_cart=5, purchase=10
    Returns list of (productId, score) sorted desc
    """
    weights = {"view": 1, "click": 2, "add_to_cart": 5, "purchase": 10}
    events_df["weight"] = events_df["eventType"].map(weights).fillna(0)
    pop = events_df.groupby("productId")["weight"].sum().sort_values(ascending=False)
    return [{"productId": pid, "score": float(score)} for pid, score in pop.items()]

def item_item_similarity(events_df: pd.DataFrame, min_co_views=3) -> dict:
    """
    Build simple co-occurrence-based item-item similarity (cosine-like).
    We create user-item interaction matrix using weighted events (purchase/add_to_cart higher).
    Return dict {productId: [(otherProductId, score), ...], ...}
    """
    weights = {"view": 1, "click": 2, "add_to_cart": 5, "purchase": 10}
    events_df["weight"] = events_df["eventType"].map(weights).fillna(0)
    # consider only rows with userId (anonymous users cannot be used for personalization)
    df = events_df.dropna(subset=["userId"]).copy()
    if df.empty:
        return {}
    # pivot user x product
    uip = df.pivot_table(index="userId", columns="productId", values="weight", aggfunc="sum", fill_value=0)
    # compute co-occurrence via matrix multiplication
    mat = uip.T.dot(uip)  # item-item matrix
    norms = (uip.T.dot(uip)).apply(np.sqrt).diag() if False else np.sqrt(np.diag(mat.values))
    # compute similarity matrix as dot / (norm_i * norm_j)
    sim = {}
    products = list(mat.index)
    mat_values = mat.values
    for i, pid in enumerate(products):
        row = []
        for j, pid2 in enumerate(products):
            if i == j:
                continue
            denom = (norms[i] * norms[j]) if norms[i] and norms[j] else 1.0
            score = float(mat_values[i, j] / denom) if denom else 0.0
            if score > 0:
                row.append((pid2, score))
        # sort descending and filter low co-visits
        row = sorted(row, key=lambda x: x[1], reverse=True)
        sim[pid] = [{"productId": r[0], "score": r[1]} for r in row]
    return sim
