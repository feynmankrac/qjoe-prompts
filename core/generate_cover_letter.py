from pathlib import Path


def generate_cover_letter(
    cover_text: str,
    output_path: str
):
    """
    Generate standalone LaTeX cover letter file.
    """

    latex_template = f"""
\\documentclass[11pt]{{article}}
\\usepackage[margin=1in]{{geometry}}
\\usepackage{{parskip}}

\\begin{{document}}

{cover_text}

\\end{{document}}
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex_template.strip())
