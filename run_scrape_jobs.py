import sys
from connectors.internshala import search_internshala, fetch_full_description
from agent.analyzer import analyze_jd
from agent.db import init_db, insert_job

init_db()

keyword = " ".join(sys.argv[1:]) or "ai-engineer"
print(f"Searching Internshala for: {keyword}\n")

jobs = search_internshala(keyword, max_results=3)

if not jobs:
    print("No jobs found (or scraper couldn't reach the site).")
    sys.exit(0)

for job in jobs:
    print(f"Found: {job['title']} @ {job['company']}")
    description = fetch_full_description(job["url"])

    result = analyze_jd(description)
    job_id = insert_job(result, portal="internshala", url=job["url"], description=description)

    if job_id == -1:
        print("  ⚠️  Duplicate, skipped")
    else:
        print(f"  ✅ Saved — {result['match_score']}% match")