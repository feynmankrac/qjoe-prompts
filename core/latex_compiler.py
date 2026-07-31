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
        cmd = [
            "pdflatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-output-directory",
            str(output_dir),
            str(tex_path)
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        pdf_name = tex_path.stem + ".pdf"
        pdf_path = output_dir / pdf_name

        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stdout + "\n" + result.stderr,
                "cmd": " ".join(cmd),
                "pdf_expected": str(pdf_path)
            }

        if not pdf_path.exists():
            return {
                "success": False,
                "error": "PDF not generated",
                "cmd": " ".join(cmd),
                "pdf_expected": str(pdf_path),
                "stdout": result.stdout,
                "stderr": result.stderr
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