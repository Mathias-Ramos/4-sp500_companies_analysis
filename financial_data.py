# Fetch yfinance information for financial analysis
from pathlib import Path

import pandas as pd
import yfinance as yf

list_csv = Path("companies.csv")
if not list_csv.exists():
    raise SystemExit("companies.csv not found - run companies.py first.")

symbols = pd.read_csv(list_csv)["ticker"]

# Fetch ticker information (stops early on rate-limit; re-run for missing ones)
tickers = yf.Tickers(" ".join(symbols))
data = tickers.get_info(progress=True)

df = pd.DataFrame.from_dict(data, orient="index")
df.index.name = "Ticker"
df = df.dropna(axis=1, how="all")

df.to_csv("yfinance_info.csv", encoding="utf-8-sig")
print(f"{len(df)} tickers, {df.shape[1]} fields -> yfinance_info.csv")
