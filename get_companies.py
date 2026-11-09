# Get the list of S&P 500 companies and their tickers

import urllib.request
from io import BytesIO
import pandas as pd

# Scrape the Wikipedia table

url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req).read()
table = pd.read_html(BytesIO(html))[0]

# Keep the useful columns, Yahoo tickers use "-" for share classes (BRK-B)

companies = table[["Symbol", "Security", "GICS Sector", "GICS Sub-Industry"]].copy()
companies.columns = ["ticker", "name", "sector", "industry"]
companies["ticker"] = companies["ticker"].str.replace(".", "-", regex=False)

companies.to_csv("companies.csv", index=False, encoding="utf-8-sig")
print(f"{len(companies)} companies -> companies.csv")
