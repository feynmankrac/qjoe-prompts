from typing import Dict


TITLE_TOKEN = "TITLEPLACEHOLDER"


def patch_latex_cv(
    template_path: str,
    output_path: str,
    generated_content: Dict
):

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    if TITLE_TOKEN not in content:
        raise ValueError("TITLEPLACEHOLDER not found in template.")

    title = generated_content.get("cv_title")
    if not title:
        raise ValueError("cv_title missing in generated_content.")

    safe_title = (
        title.replace("&", r"\&")
             .replace("%", r"\%")
             .replace("#", r"\#")
             .replace("_", r"\_")
    )

    new_content = content.replace(TITLE_TOKEN, safe_title)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_content)
