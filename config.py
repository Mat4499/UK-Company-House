import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

KEYWORDS = ["bidco", "midco", "topco", "propco", "holdco", "opco", "holdings", "spv", "uk"]
WORK_HOURS = range(7, 18)  # 7am–6pm UK time
