import sys
from agent.analyzer import analyze_jd
from agent.db import init_db, insert_job, get_all_jobs

init_db()

path = sys.argv[1]
with open(path) as f:
    jd_text = f.read()

result = analyze_jd(jd_text)
job_id = insert_job(result, portal="internshala", description=jd_text)

if job_id == -1:
    print("\n⚠️  Duplicate — this job is already saved.")
else:
    print(f"\n✅ Saved as job ID {job_id}")

print("\n===== ALL JOBS IN DATABASE =====")
for job in get_all_jobs():
    print(f"[{job['id']}] {job['title']} @ {job['company']} — {job['match_score']}% — {job['status']}")