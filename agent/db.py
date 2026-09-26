import sqlite3
import hashlib
import json
from pathlib import Path

DB_PATH = "data/jobs.db"
SCHEMA_PATH = "db/schema.sql"


def get_connection():
    Path("data").mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def make_job_hash(title: str, company: str, location: str) -> str:
    raw = f"{title.lower().strip()}|{company.lower().strip()}|{location.lower().strip()}"
    return hashlib.sha256(raw.encode()).hexdigest()


def job_exists(job_hash: str) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM jobs WHERE job_hash = ?", (job_hash,)
    ).fetchone()
    conn.close()
    return row is not None


def insert_job(analysis: dict, portal: str = "manual", url: str = "", description: str = "") -> int:
    job_hash = make_job_hash(analysis["job_title"], analysis["company"], analysis["location"])

    if job_exists(job_hash):
        log_action("duplicate_skipped", None, f"Job already exists: {analysis['job_title']}")
        return -1

    conn = get_connection()
    cur = conn.execute(
        """INSERT INTO jobs
           (job_hash, title, company, location, work_mode, stipend, portal, url,
            description, match_score, matched_skills, missing_skills, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            job_hash,
            analysis["job_title"],
            analysis["company"],
            analysis["location"],
            analysis["work_mode"],
            analysis["stipend"],
            portal,
            url,
            description,
            analysis["match_score"],
            json.dumps(analysis["matched_skills"]),
            json.dumps(analysis["missing_skills"]),
            analysis["decision"],
        ),
    )
    job_id = cur.lastrowid
    conn.commit()
    conn.close()

    log_action("job_saved", job_id, f"{analysis['job_title']} at {analysis['company']}")
    return job_id


def log_action(action: str, job_id, details: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO audit_log (action, job_id, details) VALUES (?, ?, ?)",
        (action, job_id, details),
    )
    conn.commit()
    conn.close()


def get_all_jobs():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM jobs ORDER BY discovered_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]