import os
import requests
import datetime
import time
from twilio.rest import Client

# NOTE:
# We use ETFs as proxies for indices because Alpha Vantage does not provide historical data for major indices directly.

# QQQ  -> Proxy for NASDAQ-100 (not full NASDAQ Composite)
# SPY  -> Tracks S&P 500
# ISF.L -> Tracks FTSE 100
# EXSA.DE -> Tracks STOXX Europe 600

# Important:
# ETF price ≠ index level. ETFs are scaled versions of indices (e.g., SPY ≈ S&P 500 / 10).
# Differences arise due to: - Scaling factors, - Dividends, - Expense ratios, - Small tracking errors.

account_sid = "AC24982035d0ab691e6575ccae4e6995cf"
auth_token = os.environ.get("AUTH_TOKEN")

LIST_ETFs = ["QQQ", "SPY", "ISF.L", "EXSA.DE"]
LIST_INDICES = ["NASDAQ-100", "S&P 500", "FTSE 100", "STOXX Europe 600"]

message_core = "MAIN INDICES:\n"

for ind in LIST_ETFs:
    parameters = {
        "function": "TIME_SERIES_DAILY",
        "symbol": ind,
        "apikey": os.environ.get("STOCK_PRICE_API"),
    }
    response = requests.get("https://www.alphavantage.co/query", params=parameters)
    response.raise_for_status()
    time.sleep(1)
    open = response.json()['Time Series (Daily)'][f"{datetime.datetime.now().year}-"
                f"{datetime.datetime.now().month:02}-{(datetime.datetime.now().day - 1):02}"]["1. open"]
    close = response.json()['Time Series (Daily)'][f"{datetime.datetime.now().year}-"
                f"{datetime.datetime.now().month:02}-{(datetime.datetime.now().day - 1):02}"]["4. close"]
    if (float(close) - float(open)) / float(open) < 0:
        message_core += f"{ind} ({LIST_INDICES[LIST_ETFs.index(ind)]}) 🔻{round((float(close) - float(open)) / float(open) * 100, 2)}% - Open: {round(float(open), 2)}; Close: {round(float(close), 2)}.\n\n"
    elif (float(close) - float(open)) / float(open) > 0:
        message_core += f"{ind} ({LIST_INDICES[LIST_ETFs.index(ind)]}) 🔺{round((float(close) - float(open)) / float(open) * 100, 2)}% - Open: {round(float(open), 2)}; Close: {round(float(close), 2)}.\n\n"

message_core += "\nMAIN NEWS:\n"

parameters_news_api = {
    "apiKey": os.environ.get("NEWS_API"),
    "language": "en",
    "category": "business",
            }
response = requests.get("https://newsapi.org/v2/top-headlines", params=parameters_news_api)
response.raise_for_status()
articles = response.json()["articles"][:5]

for article in articles:
    message_core += f"Title: {article['title']}\nBrief: {article['description']}\n\n"

client = Client(account_sid, auth_token)
message = client.messages.create(
    body=message_core,
    from_="+16416663460",
    to="+33640610093",
)

message_1 = client.messages.create(
  from_="whatsapp:+14155238886",
  body=message_core,
  to="whatsapp:+33640610093"
)
