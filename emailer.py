import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from config import SMTP_USER, SMTP_PASSWORD, RECEIVER_EMAIL
import os

def send_email_with_attachment(subject, results, filename="report.csv"):
    df = pd.DataFrame(results, columns=["Date", "Company Name", "Company Number", "URL"])
    df.to_csv(filename, index=False)

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = RECEIVER_EMAIL
    msg["Subject"] = subject

    msg.attach(MIMEText("See attached report.", "plain"))

    part = MIMEBase("application", "octet-stream")
    with open(filename, "rb") as f:
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename= {filename}")
    msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

    os.remove(filename)
