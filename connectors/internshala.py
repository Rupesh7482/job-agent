import requests
from bs4 import BeautifulSoup
import time


def search_internshala(keyword: str, max_results: int = 5) -> list[dict]:
    """Search Internshala for internships matching a keyword.
    Returns a list of dicts with title, company, url."""

    keyword_slug = keyword.lower().replace(" ", "-")
    search_url = f"https://internshala.com/internships/{keyword_slug}-internship"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"⚠️  Could not reach Internshala: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    cards = soup.find_all("div", class_=lambda c: c and (
        "generic_container" in c or "pro_exclusive_container" in c
    ))

    results = []
    for card in cards[:max_results]:
        title_tag = card.find(class_="job-internship-name")
        link_tag = title_tag.find("a") if title_tag else None

        if not link_tag:
            continue

        title = link_tag.get_text(strip=True)
        url = "https://internshala.com" + link_tag.get("href", "")

        company_tag = card.find(class_=lambda c: c and "company" in c.lower())
        if not company_tag:
            company_tag = card.find("a", href=lambda h: h and "/company/" in h)

        company = company_tag.get_text(strip=True) if company_tag else "Unknown"

        results.append({
            "title": title,
            "company": company,
            "url": url,
        })
        time.sleep(1)

    return results


def fetch_full_description(url: str) -> str:
    """Fetch the full job description text from an Internshala listing page."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"[Could not fetch description: {e}]"

    soup = BeautifulSoup(response.text, "html.parser")
    body = soup.find(id="internship_details") or soup.find(class_="internship_details")
    if body:
        return body.get_text(separator="\n", strip=True)
    return soup.get_text(separator="\n", strip=True)[:3000]