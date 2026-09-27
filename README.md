
Fill in `data/master_resume.json` with your real details.

## Usage

**Analyze a single job description:**
```bash
python run_analyze.py data/sample_jds/jd1.txt
```

**Analyze and save to the database:**
```bash
python run_save_job.py data/sample_jds/jd1.txt
```

**Generate a tailored resume PDF:**
```bash
python run_generate_resume.py
```

**Ask an application question:**
```bash
python run_ask_question.py "What is your notice period?"
```

**Scrape and analyze jobs from Internshala:**
```bash
python run_scrape_jobs.py "AI Engineer"
```

**View the audit log:**
```bash
python run_audit_log.py
```

**Launch the dashboard:**
```bash
streamlit run dashboard/app.py
```

## Design decisions

- **Approval-first, not auto-apply.** The agent prepares everything (scores, resumes, answers) but never submits applications automatically — avoiding ToS violations and keeping the human in control.
- **No fabricated facts.** The resume generator only reorders/rephrases real data from `master_resume.json`. The Q&A module explicitly returns "needs your input" rather than inventing an answer.
- **Score computed in code, not by the LLM.** The match score is `matched_skills ÷ required_skills × 100`, calculated in Python — not asked from the AI — for consistency and explainability.
- **Duplicate prevention via hashing.** A SHA-256 hash of title+company+location prevents the same job being saved twice, even across different sources.
- **Graceful degradation.** The scraper wraps each job in its own try/except, so one failure (e.g. a busy LLM server) doesn't crash a whole batch run.
- **Auto-retry on LLM errors.** Gemini API calls automatically retry with backoff on temporary server issues (503s).

## Known limitations

- The Internshala scraper occasionally shows "Unknown" for company name — inconsistent HTML structure across listing types.
- Only Internshala is scraped currently; other portals (Wellfound, LinkedIn, etc.) are designed for via the same connector interface but not yet implemented.
- No email/HR outreach module yet (out of scope for this submission — focused on Section 1 of the original spec: job search, resume customization, and applications).

## Author

Rupesh — B.Tech AI & ML, VIT Chennai