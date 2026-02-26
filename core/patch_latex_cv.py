from typing import List, Dict


START_MARKER = "% === PROJECTS_START ==="
END_MARKER = "% === PROJECTS_END ==="


def format_project_latex(project: Dict) -> str:
    """
    Convert one project dict to LaTeX block.
    Expects:
    {
        "title": "...",
        "bullets": [...]
    }
    """

    lines = []
    lines.append(r"\textbf{" + project["title"] + r"}")
    lines.append(r"\begin{itemize}")

    for bullet in project["bullets"]:
        lines.append(r"\item " + bullet)

    lines.append(r"\end{itemize}")
    lines.append("")

    return "\n".join(lines)


def patch_latex_cv(
    tex_path: str,
    selected_projects: List[Dict],
    output_path: str = None
):
    """
    Replace the content between PROJECTS_START and PROJECTS_END
    with selected projects formatted in LaTeX.
    """

    with open(tex_path, "r", encoding="utf-8") as f:
        content = f.read()

    if START_MARKER not in content or END_MARKER not in content:
        raise ValueError("Markers not found in LaTeX file.")

    before, rest = content.split(START_MARKER)
    middle, after = rest.split(END_MARKER)

    # Generate new projects LaTeX
    projects_blocks = []
    for project in selected_projects:
        projects_blocks.append(format_project_latex(project))

    new_middle = "\n" + START_MARKER + "\n\n" + "\n".join(projects_blocks) + "\n" + END_MARKER

    new_content = before + new_middle + after

    if output_path is None:
        output_path = tex_path

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(new_content)
