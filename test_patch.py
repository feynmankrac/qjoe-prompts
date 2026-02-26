from core.patch_latex_cv import patch_latex_cv

patch_latex_cv(
    template_path="templates/cv_market_risk.tex",
    output_path="generated_cv.tex",
    generated_content={
        "cv_title": "Quantitative Market Risk Analyst"
    }
)

print("Patch completed.")
