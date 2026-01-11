from config import KEYWORDS

def has_keyword(company_name):
    """Check if company name contains any keywords and return the matched keyword"""
    matched_keywords = [kw for kw in KEYWORDS if kw.lower() in company_name.lower()]
    return matched_keywords if matched_keywords else None

def has_foreign_director(officers):
    """Check if company has foreign directors and return their countries"""
    foreign_countries = []
    for officer in officers:
        country = officer.get("address", {}).get("country")
        if country and country != "United Kingdom" and country not in foreign_countries:
            foreign_countries.append(country)
    return foreign_countries if foreign_countries else None

def has_corporate_owner(ownerships):
    """Check if company has corporate owners"""
    return any(owner.get("kind") == "corporate-entity-person-with-significant-control" for owner in ownerships)

def meets_criteria(company, officers, ownerships):
    """
    Check if company meets any criteria and return (meets, reasons)
    Returns tuple: (bool, str) where str contains reason(s) for selection
    """
    reasons = []
    
    # Check for keywords in company name
    matched_keywords = has_keyword(company["company_name"])
    if matched_keywords:
        reasons.append(f"Keywords: {', '.join(matched_keywords).upper()}")
    
    # Check for foreign directors
    foreign_countries = has_foreign_director(officers)
    if foreign_countries:
        reasons.append(f"Foreign Directors: {', '.join(foreign_countries)}")
    
    # Check for corporate ownership
    if has_corporate_owner(ownerships):
        reasons.append("Corporate Ownership")
    
    if reasons:
        return True, " | ".join(reasons)
    else:
        return False, ""
