import sys
from agent.analyzer import analyze_jd

path = sys.argv[1]
with open(path) as f:
    jd_text = f.read()

r = analyze_jd(jd_text)

print("\n===== RESULT =====")
print("Title      :", r["job_title"])
print("Company    :", r["company"])
print("Location   :", r["location"], "|", r["work_mode"])
print("Stipend    :", r["stipend"])
print("Score      :", r["match_score"], "%")
print("Decision   :", r["decision"])
print("Matched    :", ", ".join(r["matched_skills"]))
print("Missing    :", ", ".join(r["missing_skills"]))
print("Note       :", r["note"])
