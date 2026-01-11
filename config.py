import os
from dotenv import load_dotenv

load_dotenv()

# Companies House API
API_KEY = os.getenv("API_KEY") or os.getenv("COMPANIES_HOUSE_API_KEY")

# Filter keywords
KEYWORDS = ["bidco", "midco", "topco", "propco", "holdco", "opco", "holdings", "spv", "uk"]

# Business hours (UK time)
WORK_HOURS = range(7, 18)  # 7am–6pm UK time
