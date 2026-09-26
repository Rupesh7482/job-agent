import json
from agent.llm import ask_json, CONFIG

PROMPT = """You are a careful recruiter assistant.
Compare the JOB DESCRIPTION with the CANDIDATE RESUME.

Return JSON only, with exactly these keys:
- job_title (string)
- company (string, "unknown" if not stated)
- location (string)
- work_mode ("remote", "hybrid", "onsite" or "unknown")
- stipend (string, "unknown" if not stated)
- required_skills (list of short skill names the job requires)
- matched_skills (required skills the candidate clearly has)
- missing_skills (required skills the candidate does not show)
- note (one sentence on overall fit)

Rules:
- Mark a skill as matched ONLY if the resume clearly shows it.
- Never invent skills or experience for the candidate.
- Every matched or missing skill must come from required_skills.

JOB DESCRIPTION:
{jd}

CANDIDATE RESUME:
{resume}
"""


def load_resume(path="data/master_resume.json"):
    with open(path) as f:
        return json.load(f)


def analyze_jd(jd_text: str) -> dict:
    resume = load_resume()
    prompt = PROMPT.format(jd=jd_text, resume=json.dumps(resume, indent=2))
    result = ask_json(prompt)

    required = [s.lower() for s in result.get("required_skills", [])]
    matched = [s for s in result.get("matched_skills", []) if s.lower() in required]

    score = round(100 * len(matched) / len(required), 1) if required else 0.0

    result["matched_skills"] = matched
    result["match_score"] = score
    result["decision"] = (
        "relevant" if score >= CONFIG["match_threshold"] else "skipped"
    )
    return result
