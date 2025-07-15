import ast
import re
import pandas as pd

def to_snake_case(name):
    # Replace spaces/hyphens with underscores, remove non-alphanum, and lower case
    name = re.sub(r'[\s\-]+', '_', name)
    name = re.sub(r'[^a-zA-Z0-9_]', '', name)
    return name.lower()


def parse_links(val):
    if isinstance(val, list):
        return val
    if pd.isnull(val):
        return []
    val = str(val).strip()
    # Try parsing as Python list
    try:
        parsed = ast.literal_eval(val)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed]
    except Exception:
        pass
    # Fallback: split by comma
    return [s.strip() for s in val.split(',') if s.strip()]

def prepare_llm_input(problem_scraped, additional_refs):
    prompt = (
        f"**{problem_scraped['title']}**\n\n"
        f"{problem_scraped['statement']}\n\n"
        f"**Input Specification:**\n{problem_scraped['input_spec']}\n\n"
        f"**Output Specification:**\n{problem_scraped['output_spec']}\n"
    )
    if problem_scraped.get("note_text"):
        prompt += f"\n**Note:**\n{problem_scraped['note_text']}\n"

    # Additional references
    context_text = []
    for idx, ref in enumerate(additional_refs, 1):
        snippet = ref.get("snippet", "")
        if snippet:
            context_text.append(f"---\nContext Resource #{idx}:\n{snippet.strip()}\n")
    context_block = "\n".join(context_text) if context_text else ""

    return {
        "prompt": prompt,
        "context": context_block,
        "samples": problem_scraped.get("samples", [])
    }
