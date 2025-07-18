import requests
from datetime import datetime
from config import API_KEY

BASE_URL = "https://api.company-information.service.gov.uk"

def get_newly_formed_companies(date_str=None):
    """
    Fetch all companies formed on the given date (default: today), using pagination.
    """
    if not date_str:
        date_str = datetime.today().strftime("%Y-%m-%d")

    all_companies = []
    start = 0
    page_size = 100

    while True:
        params = {
            "incorporated_from": date_str,
            "incorporated_to": date_str,
            "start_index": start,
            "size": page_size
        }

        response = requests.get(
            f"{BASE_URL}/advanced-search/companies",
            auth=(API_KEY, ""),
            params=params
        )

        if response.status_code != 200:
            print(f"❌ Failed to fetch companies (status {response.status_code})")
            break

        data = response.json()
        items = data.get("items", [])
        if not items:
            break

        print(f"📦 Fetched {len(items)} companies from index {start}")
        all_companies.extend(items)
        start += page_size

    print(f"✅ Total companies fetched for {date_str}: {len(all_companies)}")
    return all_companies


def get_company_details(company_number):
    url = f"{BASE_URL}/company/{company_number}"
    r = requests.get(url, auth=(API_KEY, ""))
    return r.json()


def get_officers(company_number):
    url = f"{BASE_URL}/company/{company_number}/officers"
    r = requests.get(url, auth=(API_KEY, ""))
    return r.json().get("items", [])


def get_ownership(company_number):
    url = f"{BASE_URL}/company/{company_number}/persons-with-significant-control"
    r = requests.get(url, auth=(API_KEY, ""))
    return r.json().get("items", [])
