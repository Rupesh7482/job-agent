import requests
from bs4 import BeautifulSoup
import time


def search_internshala(keyword: str, max_results: int = 5) -> list[dict]:
    """Search Internshala for internships matching a keyword.
    Returns a list of dicts with title, company, url, and raw description text."""

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
    listings = soup.select("div.individual_internship")[:max_results]

    results = []
    for listing in listings:
        title_tag = listing.select_one("h3.job-internship-name a")
        company_tag = listing.select_one("p.company-name")

        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        company = company_tag.get_text(strip=True) if company_tag else "Unknown"
        url = "https://internshala.com" + title_tag.get("href", "")

        results.append({
            "title": title,
            "company": company,
            "url": url,
        })
        time.sleep(1)  # be polite, don't hammer the server

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
    body = soup.select_one("div.internship_details")
    if body:
        return body.get_text(separator="\n", strip=True)
    return soup.get_text(separator="\n", strip=True)[:3000]
