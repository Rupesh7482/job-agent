import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
import pandas as pd
from agent.db import init_db, get_all_jobs, insert_job
from agent.analyzer import analyze_jd
from agent.resume_builder import generate_resume_pdf
from agent.qa_answerer import answer_question

st.set_page_config(
    page_title="Job Automation Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# ---------- Sidebar navigation ----------
st.sidebar.markdown("## 🤖 Job Automation Agent")
st.sidebar.caption("AI-powered job search assistant")
st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate",
    ["📊 Dashboard", "➕ Analyze New Job", "📋 All Jobs", "💬 Ask a Question"],
    label_visibility="collapsed",
)

st.sidebar.divider()
st.sidebar.caption("Built with Gemini, SQLite, LaTeX & Streamlit")

jobs = get_all_jobs()


def status_badge(status: str) -> str:
    colors = {"relevant": "🟢", "skipped": "🔴"}
    return f"{colors.get(status, '⚪')} {status.title()}"


# ---------- PAGE: Dashboard ----------
if page == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.caption("Live overview of your job search pipeline")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📁 Total Jobs", len(jobs))
    col2.metric("🟢 Relevant", sum(1 for j in jobs if j["status"] == "relevant"))
    col3.metric("🔴 Skipped", sum(1 for j in jobs if j["status"] == "skipped"))
    avg_score = round(sum(j["match_score"] for j in jobs) / len(jobs), 1) if jobs else 0
    col4.metric("📈 Avg Match", f"{avg_score}%")

    st.divider()

    if jobs:
        st.subheader("Match Score Distribution")
        df = pd.DataFrame(jobs)
        chart_data = df[["title", "match_score"]].set_index("title")
        st.bar_chart(chart_data, height=300)

        st.subheader("Jobs by Portal")
        portal_counts = df["portal"].value_counts()
        st.bar_chart(portal_counts, height=250)
    else:
        st.info("No data yet — analyze a job to see charts here.")

# ---------- PAGE: Analyze New Job ----------
elif page == "➕ Analyze New Job":
    st.title("➕ Analyze a New Job")
    st.caption("Paste a job description to score it against your resume")

    jd_text = st.text_area("Job description", height=250, placeholder="Paste the full job posting here...")

    col1, col2 = st.columns([1, 4])
    with col1:
        analyze_clicked = st.button("🔍 Analyze & Save", type="primary", use_container_width=True)

    if analyze_clicked:
        if jd_text.strip():
            try:
                with st.spinner("🤔 Analyzing with Gemini..."):
                    result = analyze_jd(jd_text)
                    job_id = insert_job(result, portal="manual", description=jd_text)

                if job_id == -1:
                    st.warning("⚠️ This job is already in the database (duplicate).")
                else:
                    st.success(f"✅ Saved: **{result['job_title']}** at **{result['company']}**")
                    score = result["match_score"]
                    st.progress(min(score / 100, 1.0), text=f"Match Score: {score}%")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**✅ Matched Skills**")
                        for s in result["matched_skills"]:
                            st.markdown(f"- {s}")
                    with col2:
                        st.markdown("**❌ Missing Skills**")
                        for s in result["missing_skills"]:
                            st.markdown(f"- {s}")

                    st.info(f"💬 {result['note']}")
            except Exception:
                st.error("⚠️ Gemini is temporarily busy. Please click 'Analyze & Save' again in a few seconds.")
        else:
            st.error("Please paste a job description first.")

# ---------- PAGE: All Jobs ----------
elif page == "📋 All Jobs":
    st.title("📋 All Jobs")
    st.caption(f"{len(jobs)} jobs tracked")

    if jobs:
        filter_status = st.selectbox("Filter by status", ["All", "relevant", "skipped"])
        filtered = jobs if filter_status == "All" else [j for j in jobs if j["status"] == filter_status]

        for job in filtered:
            with st.expander(f"{status_badge(job['status'])} — {job['title']} @ {job['company']} — {job['match_score']}%"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Location:** {job['location']} ({job['work_mode']})")
                    st.write(f"**Stipend:** {job['stipend']}")
                    st.write(f"**Portal:** {job['portal']}")
                with col2:
                    st.write(f"**Matched:** {job['matched_skills']}")
                    st.write(f"**Missing:** {job['missing_skills']}")

                if job.get("url"):
                    st.markdown(f"[🔗 View original posting]({job['url']})")

                if st.button("📄 Generate Tailored Resume", key=f"resume_{job['id']}"):
                    try:
                        with st.spinner("Generating PDF..."):
                            pdf_path = generate_resume_pdf(f"resume_job_{job['id']}")
                        st.success(f"✅ Saved to `{pdf_path}`")
                    except Exception:
                        st.error("⚠️ Could not generate PDF. Try again.")
    else:
        st.info("No jobs yet — go to **Analyze New Job** to get started.")

# ---------- PAGE: Ask a Question ----------
elif page == "💬 Ask a Question":
    st.title("💬 Ask an Application Question")
    st.caption("Answered from your verified knowledge base — never guesses")

    question = st.text_input("Question", placeholder="e.g. What is your notice period?")

    if st.button("Ask", type="primary"):
        if question.strip():
            try:
                with st.spinner("Checking verified facts..."):
                    result = answer_question(question)

                if result["needs_user_confirmation"]:
                    st.warning(f"⚠️ **Not found in verified facts.** {result['reason']}")
                    st.caption("Add this to `data/knowledge_base.json` to teach the agent.")
                else:
                    st.success(f"✅ **Answer:** {result['answer']}")
                    st.caption(result["reason"])
            except Exception:
                st.error("⚠️ Gemini is temporarily busy. Please click 'Ask' again in a few seconds.")
        else:
            st.error("Please type a question first.")