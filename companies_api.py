import requests
import time
from datetime import datetime
from config import API_KEY

BASE_URL = "https://api.company-information.service.gov.uk"

# Rate limiting: Companies House API allows 600 requests per 5 minutes
# That's 120 requests per minute, or 1 request per 0.5 seconds
# Using 0.6 seconds to stay safely under the limit with some buffer
REQUEST_DELAY = 0.6  # seconds between requests

def get_newly_formed_companies(date_str=None, limit_first_page_only=False):
    """
    Fetch all companies formed on the given date (default: today), using pagination.
    
    Args:
        date_str: Date string in YYYY-MM-DD format (default: today)
        limit_first_page_only: If True, only fetch first page (useful for testing)
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
            # If we already have some companies, this might just mean we've reached the end
            if all_companies and response.status_code in [500, 416]:
                print(f"⚠️  API returned {response.status_code} - likely reached end of results")
            else:
                print(f"❌ Failed to fetch companies (status {response.status_code})")
            break

        data = response.json()
        items = data.get("items", [])
        if not items:
            break

        print(f"📦 Fetched {len(items)} companies from index {start}")
        all_companies.extend(items)
        
        # Stop after first page if testing mode enabled
        if limit_first_page_only:
            print(f"⚠️  TEST MODE: Limited to first page only ({len(all_companies)} companies)")
            break
        
        start += page_size

    print(f"✅ Total companies fetched for {date_str}: {len(all_companies)}")
    return all_companies


def get_company_details(company_number):
    url = f"{BASE_URL}/company/{company_number}"
    r = requests.get(url, auth=(API_KEY, ""))
    return r.json()


def get_officers(company_number):
    """Fetch officers with retry logic for rate limiting"""
    url = f"{BASE_URL}/company/{company_number}/officers"
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            time.sleep(REQUEST_DELAY)  # Rate limiting delay
            r = requests.get(url, auth=(API_KEY, ""))
            
            if r.status_code == 429:
                # Rate limited, wait and retry
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                print(f"⚠️ Rate limited for officers {company_number}. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue
            
            if r.status_code != 200:
                print(f"⚠️ Failed to fetch officers for {company_number} (status {r.status_code})")
                return []
            
            return r.json().get("items", [])
        except Exception as e:
            print(f"⚠️ Error fetching officers for {company_number}: {e}")
            return []
    
    print(f"⚠️ Failed to fetch officers for {company_number} after {max_retries} retries")
    return []


def get_ownership(company_number):
    """Fetch ownership with retry logic for rate limiting"""
    url = f"{BASE_URL}/company/{company_number}/persons-with-significant-control"
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            time.sleep(REQUEST_DELAY)  # Rate limiting delay
            r = requests.get(url, auth=(API_KEY, ""))
            
            if r.status_code == 429:
                # Rate limited, wait and retry
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                print(f"⚠️ Rate limited for ownership {company_number}. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue
            
            if r.status_code != 200:
                print(f"⚠️ Failed to fetch ownership for {company_number} (status {r.status_code})")
                return []
            
            return r.json().get("items", [])
        except Exception as e:
            print(f"⚠️ Error fetching ownership for {company_number}: {e}")
            return []
    
    print(f"⚠️ Failed to fetch ownership for {company_number} after {max_retries} retries")
    return []
