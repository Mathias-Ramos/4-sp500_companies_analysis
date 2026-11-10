# Fetch yfinance information for financial analysis
# One CSV per dataset in ./data (long format: one row per ticker x date/period)
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

list_csv = Path("data/raw/companies.csv")
if not list_csv.exists():
    raise SystemExit("companies.csv not found - run companies.py first.")

OUT = Path("data/raw/")
OUT.mkdir(exist_ok=True)
SLEEP = 0.1   # seconds between tickers (avoids rate limiting)
LIMIT = None  # e.g. 10 to test quickly

symbols = pd.read_csv(list_csv)["ticker"].dropna().unique().tolist()
if LIMIT:
    symbols = symbols[:LIMIT]

# ------------------------------------------------------------------ what to retrieve
# ticker.info: output column -> info key
INFO_FIELDS = {
    "pe": "trailingPE",
    "forward_pe": "forwardPE",
    "ebitda": "ebitda",
    "sector": "sector",
    "industry": "industry",
    "currency": "currency",
    "market_cap": "marketCap",
}

# statements: output column -> row label in yfinance
INCOME_FIELDS = {
    "revenue": "Total Revenue",
    "ebit": "EBIT",
    "ebitda": "EBITDA",
    "tax_provision": "Tax Provision",
    "pretax_income": "Pretax Income",
    "net_income": "Net Income",
    "diluted_eps": "Diluted EPS",
}
BALANCE_FIELDS = {
    "total_debt": "Total Debt",
    "cash_and_equivalents": "Cash And Cash Equivalents",
    "stockholders_equity": "Stockholders Equity",
}
CASHFLOW_FIELDS = {
    "operating_cash_flow": "Operating Cash Flow",
    "capital_expenditure": "Capital Expenditure",
}


# ------------------------------------------------------------------ one function per dataset
def get_info(t):
    info = t.info
    return pd.DataFrame([{col: info.get(key) for col, key in INFO_FIELDS.items()}])


def get_prices(t):
    h = t.history(period="10y", interval="1wk", auto_adjust=True)
    out = h[["Close"]].rename(columns={"Close": "adj_close"})
    out.index = out.index.tz_localize(None)
    return out.rename_axis("date").reset_index()


def statement(df, fields):
    """yfinance statement (rows = items, columns = dates) -> one row per date."""
    out = pd.DataFrame({col: df.loc[label] for col, label in fields.items() if label in df.index})
    if out.empty:
        return None
    return out.rename_axis("date").reset_index()


def get_valuation(t):
    return t.get_valuation_measures().reset_index()


TABLES = {
    "financials": get_info,                                    # ticker.info
    "prices_weekly": get_prices,                               # ticker.history()
    "income_stmt": lambda t: statement(t.income_stmt, INCOME_FIELDS),
    "balance_sheet": lambda t: statement(t.balance_sheet, BALANCE_FIELDS),
    "cashflow": lambda t: statement(t.cashflow, CASHFLOW_FIELDS),
    "valuation_measures": get_valuation,                       # ticker.get_valuation_measures()
    "earnings_estimate": lambda t: t.earnings_estimate.reset_index(),
    "revenue_estimate": lambda t: t.revenue_estimate.reset_index(),
    "eps_trend": lambda t: t.eps_trend.reset_index(),
    "eps_revisions": lambda t: t.eps_revisions.reset_index(),
}

if not hasattr(yf.Ticker, "get_valuation_measures"):
    print("WARNING: this yfinance version has no get_valuation_measures() - skipped. "
          "Try: pip install -U yfinance")
    del TABLES["valuation_measures"]


def rate_limited(e):
    return "ratelimit" in type(e).__name__.lower() or "too many requests" in str(e).lower()


# ------------------------------------------------------------------ fetch
frames = {name: [] for name in TABLES}
failures = {name: 0 for name in TABLES}
stop = False

for i, sym in enumerate(symbols, 1):
    t = yf.Ticker(sym)
    for name, fetch in TABLES.items():
        try:
            df = fetch(t)
            if df is not None and not df.empty:
                df.insert(0, "ticker", sym)
                frames[name].append(df)
        except Exception as e:
            if rate_limited(e):
                print(f"Rate limited at {sym} - stopping, saving what we have.")
                stop = True
                break
            failures[name] += 1
    if stop:
        break
    print(f"[{i}/{len(symbols)}] {sym}")
    time.sleep(SLEEP)

# ------------------------------------------------------------------ export
for name, parts in frames.items():
    if not parts:
        print(f"{name}: no data")
        continue
    df = pd.concat(parts, ignore_index=True)
    df.to_csv(OUT / f"{name}.csv", index=False, encoding="utf-8-sig")
    print(f"{name}: {len(df)} rows, {failures[name]} failed tickers -> {OUT / name}.csv")