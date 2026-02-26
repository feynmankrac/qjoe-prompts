from typing import List, Dict


# ===============================
# Weight configuration (modifiable)
# ===============================

WEIGHTS = {
    "role_family_match": 5,
    "asset_class_match": 4,
    "signal_match": 3,
    "tool_match": 2,
    "intensity_bonus": 1,
}


# ===============================
# Helper functions
# ===============================

def score_project(project: Dict, job: Dict) -> int:
    score = 0

    # Role family match
    if job.get("role_family") and job["role_family"] in project.get("role_families", []):
        score += WEIGHTS["role_family_match"]

    # Asset class match
    for asset in job.get("asset_classes", []):
        if asset in project.get("asset_classes", []):
            score += WEIGHTS["asset_class_match"]

    # Signals match
    for signal in job.get("signals_for_fit", []):
        if signal in project.get("signals", []):
            score += WEIGHTS["signal_match"]

    # Tools match
    for tool in job.get("tools", []):
        if tool in project.get("tools", []):
            score += WEIGHTS["tool_match"]

    # Intensity proximity
    job_intensity = job.get("quant_intensity", 0)
    project_intensity = project.get("intensity", 0)

    if project_intensity >= job_intensity and job_intensity >= 6:
        score += WEIGHTS["intensity_bonus"]

    return score


# ===============================
# Main function
# ===============================

def select_projects(
    job_json_normalized: Dict,
    projects_index: Dict[str, Dict],
    top_k: int = 4
) -> List[str]:

    scored_projects = []

    for project_id, project_data in projects_index.items():
        score = score_project(project_data, job_json_normalized)
        scored_projects.append((project_id, score))

    # Sort by score descending, then stable alphabetical fallback
    scored_projects.sort(key=lambda x: (-x[1], x[0]))

    # Filter only positive scores
    positive = [pid for pid, score in scored_projects if score > 0]

    # If fewer than top_k positive matches,
    # fallback to highest scored even if zero
    if len(positive) >= top_k:
        return positive[:top_k]
    else:
        return [pid for pid, _ in scored_projects[:top_k]]
