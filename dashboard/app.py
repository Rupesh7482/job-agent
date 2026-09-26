import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
from agent.db import init_db, get_all_jobs, insert_job
from agent.analyzer import analyze_jd
from agent.resume_builder import generate_resume_pdf

st.set_page_config(page_title="Job Automation Agent", layout="wide")
init_db()

st.title("🤖 Job Automation Agent")

jobs = get_all_jobs()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Jobs", len(jobs))
col2.metric("Relevant", sum(1 for j in jobs if j["status"] == "relevant"))
col3.metric("Skipped", sum(1 for j in jobs if j["status"] == "skipped"))
avg_score = round(sum(j["match_score"] for j in jobs) / len(jobs), 1) if jobs else 0
col4.metric("Avg Match Score", f"{avg_score}%")

st.divider()

st.subheader("➕ Analyze a New Job")
jd_text = st.text_area("Paste job description here", height=200)

if st.button("Analyze & Save"):
    if jd_text.strip():
        with st.spinner("Analyzing with Gemini..."):
            result = analyze_jd(jd_text)
            job_id = insert_job(result, portal="manual", description=jd_text)
        if job_id == -1:
            st.warning("⚠️ This job is already in the database (duplicate).")
        else:
            st.success(f"✅ Saved: {result['job_title']} at {result['company']} — {result['match_score']}% match")
        st.rerun()
    else:
        st.error("Please paste a job description first.")

st.divider()

st.subheader("📋 All Jobs")
if jobs:
    for job in jobs:
        with st.expander(f"{job['title']} @ {job['company']} — {job['match_score']}% — {job['status']}"):
            st.write(f"**Location:** {job['location']} | {job['work_mode']}")
            st.write(f"**Stipend:** {job['stipend']}")
            st.write(f"**Matched Skills:** {job['matched_skills']}")
            st.write(f"**Missing Skills:** {job['missing_skills']}")
            if st.button(f"Generate Resume for Job #{job['id']}", key=f"resume_{job['id']}"):
                with st.spinner("Generating PDF..."):
                    pdf_path = generate_resume_pdf(f"resume_job_{job['id']}")
                st.success(f"Resume saved to: {pdf_path}")
else:
    st.info("No jobs yet — paste a job description above to get started.")
