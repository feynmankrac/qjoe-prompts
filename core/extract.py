import json
from typing import Dict


def load_prompt(prompt_path: str) -> str:
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def call_llm(prompt_text: str) -> Dict:
    raise NotImplementedError("LLM call not implemented yet.")


def extract_job(raw_text: str) -> Dict:

    prompt_text = load_prompt("prompts/01_extract_job.md")

    full_prompt = prompt_text + "\n\nJOB_TEXT:\n" + raw_text

    response = call_llm(full_prompt)

    return response
