import json
from agent.llm import ask_json

KB_PATH = "data/knowledge_base.json"

PROMPT = """You are helping a candidate answer a job application question.
Use ONLY the VERIFIED FACTS below. Never invent information.

Return JSON with exactly these keys:
- answer (string — the answer if you can find it in verified facts, else empty string)
- confident (true or false)
- reason (one sentence explaining your decision)

VERIFIED FACTS:
{facts}

QUESTION:
{question}
"""


def load_kb(path: str = KB_PATH) -> dict:
    with open(path) as f:
        return json.load(f)


def answer_question(question: str) -> dict:
    facts = load_kb()
    prompt = PROMPT.format(facts=json.dumps(facts, indent=2), question=question)
    result = ask_json(prompt)

    if not result.get("confident") or not result.get("answer", "").strip():
        result["needs_user_confirmation"] = True
        result["answer"] = None
    else:
        result["needs_user_confirmation"] = False

    return result