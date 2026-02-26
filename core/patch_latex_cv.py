from typing import Dict
from pathlib import Path


MARKERS = {
    "COVER": ("% === COVER_LETTER_START ===", "% === COVER_LETTER_END ==="),
    "TITLE": ("% === CV_TITLE_START ===", "% === CV_TITLE_END ==="),
}


def replace_section(content: str, start_marker: str, end_marker: str, new_text: str) -> str:
    if start_marker not in content or end_marker not in content:
        raise ValueError(f"Markers {start_marker} / {end_marker} not found.")

    before, rest = content.split(start_marker)
    middle, after = rest.split(end_marker)

    new_middle = f"\n{start_marker}\n{new_text}\n{end_marker}"
    return before + new_middle + after


def patch_latex_cv(
    template_path: str,
    output_path: str,
    generated_content: Dict
):
    """
    Inject dynamic content into LaTeX template.

    generated_content expects:
    {
        "cv_title": str,
        "cover_letter_en": str
    }
    """

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Inject title
    if generated_content.get("cv_title"):
        content = replace_section(
            content,
            *MARKERS["TITLE"],
            new_text=generated_content["cv_title"]
        )

    # Inject cover letter
    if generated_content.get("cover_letter_en"):
        content = replace_section(
            content,
            *MARKERS["COVER"],
            new_text=generated_content["cover_letter_en"]
        )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
