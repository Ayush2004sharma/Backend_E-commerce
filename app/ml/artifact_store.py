# app/ml/artifact_store.py
import os, json
from pathlib import Path

ARTIFACT_DIR = Path("./ml_artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

def write_json(name: str, obj):
    path = ARTIFACT_DIR / name
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f)

def read_json(name: str):
    path = ARTIFACT_DIR / name
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
