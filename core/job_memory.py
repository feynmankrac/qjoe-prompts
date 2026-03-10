import json
import hashlib
from pathlib import Path

MEMORY_PATH = Path("artifacts/jobs_memory.json")


def load_memory():
    if MEMORY_PATH.exists():
        with open(MEMORY_PATH, "r") as f:
            return set(json.load(f))
    return set()


def save_memory(memory):
    with open(MEMORY_PATH, "w") as f:
        json.dump(list(memory), f)


def hash_job(text):
    return hashlib.sha1(text.encode()).hexdigest()
