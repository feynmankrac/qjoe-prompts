import subprocess
from pathlib import Path


def compile_latex(tex_path: str, output_dir: str = None) -> Dict:
    """
    Compile LaTeX file into PDF using pdflatex.
    """

    tex_path = Path(tex_path)

    if output_dir is None:
        output_dir = tex_path.parent

    try:
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-output-directory",
                str(output_dir),
                str(tex_path)
            ],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr
            }

        pdf_path = tex_path.with_suffix(".pdf")

        return {
            "success": True,
            "pdf_path": str(pdf_path)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
