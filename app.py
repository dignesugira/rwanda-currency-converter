import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()
api_key = os.getenv("EXCHANGE_API_KEY")

app = Flask(__name__)
EAST_AFRICA = ["RWF", "KESH", "UGX", "TZS", "BIF", "SSP"]


@app.route("/")
def home():
    search = request.args.get("search", "").upper()
    region = request.args.get("region", "all")
    sort = request.args.get("sort", "code")
    try:
        data = requests.get(f"https://v6.exchangerate-api.com/v6/{api_key}/latest/RWF", timeout=10).json()
    except requests.RequestException:
        return render_template("index.html", error="couldn't reach the exchange rate service. try again later")

    if data.get("result") != "success":
        return render_template("index.html", error="The exchange rate service returned an error:" +str(data.get("error-type")))

    rates = data["conversion_rates"]

    results = []
    for code, rate in rates.items():
        if search and search not in code:
            continue
        if region == "east" and code not in EAST_AFRICA:
            continue
        results.append((code, rate))
    
    if sort == "rate":
        results.sort(key=lambda item: item[1])
    else:
        results.sort()
    return render_template("index.html", results=results, search= search, region= region, sort= sort)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
