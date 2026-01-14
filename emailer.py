import os
import resend
import pandas as pd
import base64
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Resend
resend.api_key = os.getenv("RESEND_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "onboarding@resend.dev")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL") or os.getenv("RECIPIENT_EMAIL")

def generate_company_card(company, officers, ownerships, show_foreign_directors=True, show_corporate_owners=True, accent_color="#4CAF50"):
    """Generate HTML for a single company card"""
    company_name = company["company_name"]
    company_number = company["company_number"]
    incorporation_date = company["date_of_creation"]
    company_status = company.get("company_status", "active")
    company_type = company.get("company_type", "")
    
    html = f"""
    <div style="background-color: #1a1a1a; padding: 20px; margin-bottom: 20px; border-radius: 8px; border-left: 4px solid {accent_color};">
        <h2 style="color: #ffffff; margin-top: 0;">{company_name}</h2>
        <p style="color: #cccccc;"><strong>Company Number:</strong> {company_number}</p>
        <p style="color: #cccccc;"><strong>Incorporation Date:</strong> {incorporation_date}</p>
        <p style="color: #cccccc;"><strong>Status:</strong> {company_status}</p>
    """
    
    # Only show Type if available
    if company_type:
        html += f'<p style="color: #cccccc;"><strong>Type:</strong> {company_type}</p>'
    
    # Check for foreign directors
    if show_foreign_directors:
        foreign_directors = []
        for officer in officers:
            country = officer.get("address", {}).get("country")
            if country and country not in ["United Kingdom", "England"]:
                name = officer.get("name", "Unknown")
                foreign_directors.append((name, country))
        
        if foreign_directors:
            html += """
            <div style="background-color: #2d3748; padding: 15px; margin: 10px 0; border-radius: 5px;">
                <p style="color: #63b3ed; margin: 0 0 10px 0;"><strong>🌍 Foreign Directors:</strong></p>
                <ul style="color: #e2e8f0; margin: 0; padding-left: 20px;">
            """
            for name, country in foreign_directors:
                html += f"<li>{name} ({country}) - director</li>"
            html += "</ul></div>"
    
    # Check for corporate owners
    if show_corporate_owners:
        corporate_owners = []
        for owner in ownerships:
            if owner.get("kind") == "corporate-entity-person-with-significant-control":
                owner_name = owner.get("name", "Unknown Corporate Entity")
                corporate_owners.append(owner_name)
        
        if corporate_owners:
            html += """
            <div style="background-color: #2c5f4f; padding: 15px; margin: 10px 0; border-radius: 5px;">
                <p style="color: #68d391; margin: 0 0 10px 0;"><strong>🏛️ Corporate Owners:</strong></p>
                <ul style="color: #e2e8f0; margin: 0; padding-left: 20px;">
            """
            for owner_name in corporate_owners:
                html += f"<li>{owner_name} (Corporate Entity Person With Significant Control)</li>"
            html += "</ul></div>"
    
    html += "</div>"
    return html

def generate_html_body(detailed_results):
    """Generate rich HTML email body with companies grouped by matching criteria"""
    from filters import has_keyword, has_foreign_director, has_corporate_owner
    
    # Categorize companies
    keyword_companies = []
    foreign_director_companies = []
    corporate_owner_companies = []
    
    for item in detailed_results:
        company = item["company"]
        officers = item["officers"]
        ownerships = item["ownerships"]
        
        # Check which criteria this company matches
        has_kw = has_keyword(company["company_name"])
        has_fd = has_foreign_director(officers)
        has_co = has_corporate_owner(ownerships)
        
        # Add to appropriate categories
        if has_kw:
            keyword_companies.append(item)
        if has_fd:
            foreign_director_companies.append(item)
        if has_co:
            corporate_owner_companies.append(item)
    
    html_parts = []
    
    # Section 1: Companies with Keywords (BidCo, MidCo, HoldCo, etc.)
    # Tailwind blue-400: #40a9fa
    if keyword_companies:
        html_parts.append("""
        <div style="margin-bottom: 40px;">
            <h1 style="color: #40a9fa; border-bottom: 2px solid #40a9fa; padding-bottom: 10px;">
                📝 Companies with Keywords (BidCo, MidCo, TopCo, PropCo, HoldCo, OpCo, Holdings, SPV, UK)
            </h1>
        """)
        for item in keyword_companies:
            html_parts.append(generate_company_card(item["company"], item["officers"], item["ownerships"], accent_color="#40a9fa"))
        html_parts.append("</div>")
    
    # Section 2: Companies with Foreign Directors
    # Tailwind amber-400: #fbbf24
    if foreign_director_companies:
        html_parts.append("""
        <div style="margin-bottom: 40px;">
            <h1 style="color: #fbbf24; border-bottom: 2px solid #fbbf24; padding-bottom: 10px;">
                🌍 Companies with Foreign Directors
            </h1>
        """)
        for item in foreign_director_companies:
            html_parts.append(generate_company_card(item["company"], item["officers"], item["ownerships"], accent_color="#fbbf24"))
        html_parts.append("</div>")
    
    # Section 3: Companies with Corporate Ownership
    # Tailwind emerald-400: #34d399
    if corporate_owner_companies:
        html_parts.append("""
        <div style="margin-bottom: 40px;">
            <h1 style="color: #34d399; border-bottom: 2px solid #34d399; padding-bottom: 10px;">
                🏛️ Companies with Corporate Ownership
            </h1>
        """)
        for item in corporate_owner_companies:
            html_parts.append(generate_company_card(item["company"], item["officers"], item["ownerships"], accent_color="#34d399"))
        html_parts.append("</div>")
    
    return "".join(html_parts)

def send_email_with_attachment(subject, results, detailed_results=None, filename="companies_report.csv"):
    """Send email with CSV attachment and rich HTML body using Resend API"""
    
    if not resend.api_key:
        raise ValueError("RESEND_API_KEY environment variable not set")
    
    if not RECEIVER_EMAIL:
        raise ValueError("RECEIVER_EMAIL or RECIPIENT_EMAIL environment variable not set")
    
    # Generate CSV in memory
    df = pd.DataFrame(results, columns=[
        "Date", 
        "Company Name", 
        "Company Number", 
        "URL", 
        "Selection Reason",
        "Foreign Directors (Details)",
        "Corporate Owners (Details)"
    ])
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue()
    
    # Convert to base64 string (required by Resend)
    csv_base64 = base64.b64encode(csv_bytes).decode('utf-8')
    
    # Generate HTML body
    if detailed_results:
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #0d1117; color: #c9d1d9; }}
            </style>
        </head>
        <body>
            <p style="color: #c9d1d9;">Please find attached the Companies House report with <strong>{len(results)} matching companies</strong>.</p>
            <hr style="border: 1px solid #30363d; margin: 20px 0;">
            {generate_html_body(detailed_results)}
        </body>
        </html>
        """
    else:
        html_body = f"<p>Please find attached the Companies House report with <strong>{len(results)} matching companies</strong>.</p>"
    
    try:
        params = {
            "from": SENDER_EMAIL,
            "to": [RECEIVER_EMAIL],
            "subject": subject,
            "html": html_body,
            "attachments": [{
                "filename": filename,
                "content": csv_base64
            }]
        }
        
        response = resend.Emails.send(params)
        print(f"✅ Email sent via Resend! ID: {response['id']}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email via Resend: {e}")
        raise
