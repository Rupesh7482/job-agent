import yaml
from datetime import date
from agent.db import get_connection


def load_config(path="config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


def portal_enabled(portal: str) -> bool:
    config = load_config()
    portals = config.get("portals", {})
    return portals.get(portal, {}).get("enabled", False)


def jobs_saved_today() -> int:
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) as c FROM jobs WHERE date(discovered_at) = date('now')"
    ).fetchone()
    conn.close()
    return row["c"]


def can_save_more_today() -> bool:
    config = load_config()
    limit = config.get("limits", {}).get("max_per_day", 10)
    return jobs_saved_today() < limit


def check_before_save(portal: str) -> tuple[bool, str]:
    """Returns (allowed, reason)."""
    if not portal_enabled(portal):
        return False, f"Portal '{portal}' is disabled in config.yaml"
    if not can_save_more_today():
        return False, "Daily application limit reached"
    return True, "OK"
