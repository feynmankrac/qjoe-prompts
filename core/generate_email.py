import json
from typing import Dict


def load_prompt(prompt_path: str) -> str:
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def build_llm_input(job_json: Dict, score_result: Dict, template_result: Dict) -> str:
    payload = {
        "job_json": job_json,
        "score_result": score_result,
        "template_result": template_result
    }

    return "\n\nINPUT:\n" + json.dumps(payload, indent=2)


def call_llm(prompt_text: str) -> Dict:
    raise NotImplementedError("LLM call not implemented yet.")


def generate_email(
    job_json: Dict,
    score_result: Dict,
    template_result: Dict,
    prompt_path: str = "prompts/06_generate_email.md"
) -> Dict:

    prompt_text = load_prompt(prompt_path)
    llm_input = build_llm_input(job_json, score_result, template_result)

    full_prompt = prompt_text + llm_input

    response = call_llm(full_prompt)

    return response
