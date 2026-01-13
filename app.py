from companies_api import get_newly_formed_companies, get_company_details, get_officers, get_ownership
from filters import meets_criteria, has_keyword, has_foreign_director, has_corporate_owner
from emailer import send_email_with_attachment
from utils import get_current_uk_hour, load_previous, save_processed
from datetime import datetime

def run_report():
    if get_current_uk_hour() not in range(7, 18):
        print("⏰ Outside business hours (7 AM - 6 PM UK)")
        return

    print("🚀 Running hourly report...")
    # Set to True for faster testing, False for production
    TEST_MODE = False
    companies = get_newly_formed_companies(limit_first_page_only=TEST_MODE)
    print(f"🔍 Fetched {len(companies)} companies")

    seen = load_previous()
    results = []
    detailed_results = []  # For email body with full details

    for company in companies:
        num = company["company_number"]
        if num in seen:
            continue

        officers = get_officers(num)
        ownerships = get_ownership(num)

        meets, reason = meets_criteria(company, officers, ownerships)
        if meets:
            print(f"✅ Match: {company['company_name']} - {reason}")
            
            # Extract foreign directors details for CSV
            foreign_directors_details = []
            for officer in officers:
                country = officer.get("address", {}).get("country")
                if country and country not in ["United Kingdom", "England"]:
                    name = officer.get("name", "Unknown")
                    foreign_directors_details.append(f"{name} ({country})")
            foreign_directors_str = "; ".join(foreign_directors_details) if foreign_directors_details else ""
            
            # Extract corporate owners details for CSV
            corporate_owners_details = []
            for owner in ownerships:
                if owner.get("kind") == "corporate-entity-person-with-significant-control":
                    owner_name = owner.get("name", "Unknown Corporate Entity")
                    corporate_owners_details.append(owner_name)
            corporate_owners_str = "; ".join(corporate_owners_details) if corporate_owners_details else ""
            
            # CSV data with detailed columns
            results.append([
                company["date_of_creation"],
                company["company_name"],
                num,
                f"https://find-and-update.company-information.service.gov.uk/company/{num}",
                reason,
                foreign_directors_str,
                corporate_owners_str
            ])
            
            # Detailed data for email body
            detailed_results.append({
                "company": company,
                "officers": officers,
                "ownerships": ownerships,
                "reason": reason
            })
            
            seen.add(num)

    if results:
        print(f"📤 Sending report with {len(results)} companies")
        send_email_with_attachment("📈 Companies House Report", results, detailed_results)
        save_processed(seen)
    else:
        print("⚠️ No matching companies found.")

if __name__ == "__main__":
    run_report()
