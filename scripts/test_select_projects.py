import json
from core.select_projects import select_projects

job_json_normalized = {
  "role_family": "DATA_SCIENCE",
  "asset_classes": ["FX"],
  "signals_for_fit": ["EXECUTION_ALGO_EXPOSURE", "BUILDING_INTERNAL_TOOLS"],
  "tools": ["Python"],
  "quant_intensity": 5
}

with open("data/projects_index.json", "r", encoding="utf-8") as f:
    projects_index = json.load(f)

print(select_projects(job_json_normalized, projects_index))
