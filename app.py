import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template

load_dotenv()
api_key = os.getenv("EXCHANGE_API_KEY")

app = Flask(__name__)

@app.route("/")
def home():
    data = requests.get(f"https://v6.exchangerate-api.com/v6/34a13389ba4e16298eae5081/latest/USD")
    rates = data["conversion_rates"]
    return render_template("index.html", rates=rates)

if __name__ = "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    