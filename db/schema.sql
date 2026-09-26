CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_hash TEXT UNIQUE,
  title TEXT,
  company TEXT,
  location TEXT,
  work_mode TEXT,
  stipend TEXT,
  portal TEXT,
  url TEXT,
  description TEXT,
  match_score REAL,
  matched_skills TEXT,
  missing_skills TEXT,
  status TEXT DEFAULT 'discovered',
  discovered_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS applications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id INTEGER,
  status TEXT DEFAULT 'prepared',
  applied_at TEXT,
  result TEXT,
  FOREIGN KEY (job_id) REFERENCES jobs(id)
);

CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  action TEXT,
  job_id INTEGER,
  details TEXT,
  timestamp TEXT DEFAULT CURRENT_TIMESTAMP
);