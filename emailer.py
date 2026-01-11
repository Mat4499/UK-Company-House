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

def send_email_with_attachment(subject, results, filename="companies_report.csv"):
    """Send email with CSV attachment using Resend API (works on Railway/Render)"""
    
    if not resend.api_key:
        raise ValueError("RESEND_API_KEY environment variable not set")
    
    if not RECEIVER_EMAIL:
        raise ValueError("RECEIVER_EMAIL or RECIPIENT_EMAIL environment variable not set")
    
    # Generate CSV in memory
    df = pd.DataFrame(results, columns=["Date", "Company Name", "Company Number", "URL"])
    csv_buffer = BytesIO()
    df.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue()
    
    # Convert to base64 string (required by Resend)
    csv_base64 = base64.b64encode(csv_bytes).decode('utf-8')
    
    try:
        params = {
            "from": SENDER_EMAIL,
            "to": [RECEIVER_EMAIL],
            "subject": subject,
            "html": f"<p>Please find attached the Companies House report with <strong>{len(results)} matching companies</strong>.</p>",
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
