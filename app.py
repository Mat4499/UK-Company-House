from companies_api import get_newly_formed_companies, get_company_details, get_officers, get_ownership
from filters import meets_criteria
from emailer import send_email_with_attachment
from utils import get_current_uk_hour, load_previous, save_processed
from datetime import datetime

def run_report():
    if get_current_uk_hour() not in range(7, 18):
        print("⏰ Outside business hours (7 AM - 6 PM UK)")
        return

    print("🚀 Running hourly report...")
    companies = get_newly_formed_companies()
    print(f"🔍 Fetched {len(companies)} companies")

    seen = load_previous()
    results = []

    for company in companies:
        num = company["company_number"]
        if num in seen:
            continue

        officers = get_officers(num)
        ownerships = get_ownership(num)

        meets, reason = meets_criteria(company, officers, ownerships)
        if meets:
            print(f"✅ Match: {company['company_name']} - {reason}")
            results.append([
                company["date_of_creation"],
                company["company_name"],
                num,
                f"https://find-and-update.company-information.service.gov.uk/company/{num}",
                reason
            ])
            seen.add(num)

    if results:
        print(f"📤 Sending report with {len(results)} companies")
        send_email_with_attachment("📈 Companies House Report", results)
        save_processed(seen)
    else:
        print("⚠️ No matching companies found.")

if __name__ == "__main__":
    run_report()
