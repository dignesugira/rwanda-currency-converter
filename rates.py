import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("EXCHANGE_API_KEY")

url = f" https://v6.exchangerate-api.com/v6/34a13389ba4e16298eae5081/latest/USD"

try:
    response = requests.get(url, timeout=10)
    data = response.json()
except requests.RequestsException:
    print("exchange rate service not reachable, check yout connection")
    raise SystemExit(1)
if data["result"] != "success":
    print("Error:", data.get("error-type"))
    raise SystemExit(1)
print("rates for 1rwf updated", data["time_last_update_utc"])
for code, rate in data["conversion_rates"].items():
    print(code, rate)