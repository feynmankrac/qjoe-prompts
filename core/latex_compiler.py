from typing import Dict
import subprocess
from pathlib import Path


def compile_latex(tex_path: str, output_dir: str = None) -> Dict:

    tex_path = Path(tex_path).resolve()

    if not tex_path.exists():
        return {
            "success": False,
            "error": f"TeX file not found: {tex_path}"
        }

    if output_dir is None:
        output_dir = tex_path.parent
    else:
        output_dir = Path(output_dir).resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
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
                "error": result.stderr or result.stdout
            }

        pdf_path = output_dir / tex_path.with_suffix(".pdf").name

        if not pdf_path.exists():
            return {
                "success": False,
                "error": "PDF not generated."
            }

        return {
            "success": True,
            "pdf_path": str(pdf_path)
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
