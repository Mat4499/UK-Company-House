from config import KEYWORDS

def has_keyword(company_name):
    return any(kw.lower() in company_name.lower() for kw in KEYWORDS)

def has_foreign_director(officers):
    return any(officer.get("address", {}).get("country") != "United Kingdom" for officer in officers)

def has_corporate_owner(ownerships):
    return any(owner.get("kind") == "corporate-entity-person-with-significant-control" for owner in ownerships)

def meets_criteria(company, officers, ownerships):
    return (
        has_keyword(company["company_name"]) or
        has_foreign_director(officers) or
        has_corporate_owner(ownerships)
    )
