import os
import time
from pathlib import Path

ARTIFACTS_DIR = Path("artifacts")
DAYS = 7
NOW = time.time()

for file in ARTIFACTS_DIR.glob("*"):

    if not file.is_file():
        continue

    if file.name == "last_run.json":
        continue

    age_days = (NOW - file.stat().st_mtime) / 86400

    if age_days > DAYS:
        try:
            os.remove(file)
            print("Deleted:", file)
        except Exception as e:
            print("Failed:", file, e)
