from agent.db import get_connection

conn = get_connection()
rows = conn.execute(
    "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 20"
).fetchall()
conn.close()

print("\n===== AUDIT LOG (last 20 actions) =====")
for row in rows:
    print(f"[{row['timestamp']}] {row['action']} — {row['details']}") 
    