from typing import Dict


START_MARKER = "% === CV_TITLE_START ==="
END_MARKER = "% === CV_TITLE_END ==="


def patch_latex_cv(
    template_path: str,
    output_path: str,
    generated_content: Dict
):
    """
    Inject dynamic title into CV template.
    """

    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    if START_MARKER not in content or END_MARKER not in content:
        raise ValueError("Title markers not found in template.")

    before, rest = content.split(START_MARKER)
    middle, after = rest.split(END_MARKER)

    new_middle = f"\n{START_MARKER}\n{generated_content['cv_title']}\n{END_MARKER}"

    new_content = before + new_middle + after

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_content)
