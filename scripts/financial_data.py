# Fetch yfinance information for financial analysis
# One CSV per dataset in ./data (long format: one row per ticker x date/period)
import os
import time
from datetime import date
from pathlib import Path

import pandas as pd
import yfinance as yf

list_csv = Path("data/raw/companies.csv")
if not list_csv.exists():
    raise SystemExit("companies.csv not found - run companies.py first.")

OUT = Path(os.environ.get("OUT_DIR", "data/raw/"))
OUT.mkdir(parents=True, exist_ok=True)
SLEEP = float(os.environ.get("SLEEP", 0.1))    # seconds between tickers (avoids rate limiting)
LIMIT = int(os.environ["LIMIT"]) if "LIMIT" in os.environ else None  # e.g. 10 to test quickly

symbols = pd.read_csv(list_csv)["ticker"].dropna().unique().tolist()
if LIMIT:
    symbols = symbols[:LIMIT]

# ------------------------------------------------------------------ what to retrieve
# ticker.info: output column -> info key
INFO_FIELDS = {
    "country": "country",
    "currency": "currency",
    "market_cap": "marketCap",
    "ttm_ebitda": "ebitda",
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
    "invested_capital": "Invested Capital",
    "net_debt": "Net Debt",
    "total_assets": "Total Assets",
    "cash_and_short_term_investments": "Cash Cash Equivalents And Short Term Investments",
}
CASHFLOW_FIELDS = {
    "operating_cash_flow": "Operating Cash Flow",
    "capital_expenditure": "Capital Expenditure",
}

# valuation measures: yfinance row label -> output column
VALUATION_RENAME = {
    "Market Cap": "market_cap",
    "Enterprise Value": "enterprise_value",
    "Trailing P/E": "trailing_pe",
    "Forward P/E": "forward_pe",
    "PEG Ratio (5yr expected)": "peg_ratio",
    "Price/Sales": "price_sales",
    "Price/Book": "price_book",
    "Enterprise Value/Revenue": "ev_revenue",
    "Enterprise Value/EBITDA": "ev_ebitda",
}

# analyst estimates: yfinance column -> output column, per source table
ESTIMATE_RENAMES = {
    "earnings_estimate": {
        "avg": "eps_avg",
        "low": "eps_low",
        "high": "eps_high",
        "yearAgoEps": "eps_year_ago",
        "numberOfAnalysts": "eps_number_of_analysts",
        "growth": "eps_growth",
    },
    "revenue_estimate": {
        "avg": "revenue_avg",
        "low": "revenue_low",
        "high": "revenue_high",
        "numberOfAnalysts": "revenue_number_of_analysts",
        "yearAgoRevenue": "revenue_year_ago",
        "growth": "revenue_growth",
    },
    "eps_trend": {
        "current": "trend_current",
        "7daysAgo": "trend_7_days_ago",
        "30daysAgo": "trend_30_days_ago",
        "60daysAgo": "trend_60_days_ago",
        "90daysAgo": "trend_90_days_ago",
    },
    "eps_revisions": {
        "upLast7days": "up_last_7_days",
        "upLast30days": "up_last_30_days",
        "downLast30days": "down_last_30_days",
        "downLast7Days": "down_last_7_days",
    },
}


# ------------------------------------------------------------------ one function per dataset
def get_info(t):
    info = t.info
    return pd.DataFrame([{col: info.get(key) for col, key in INFO_FIELDS.items()}])


def get_prices(t):
    """Weekly history merged (asof) with historical valuation measures."""
    h = t.history(period="10y", interval="1wk", auto_adjust=True)
    prices = h[["Close"]].rename(columns={"Close": "adj_close"})
    prices.index = prices.index.tz_localize(None)
    prices = prices.rename_axis("date").reset_index()

    valuation = valuation_wide(t)
    if valuation is None:
        return prices
    # merge_asof requires identical datetime dtypes on both sides
    prices["date"] = prices["date"].astype("datetime64[us]")
    valuation["date"] = valuation["date"].astype("datetime64[us]")
    prices = pd.merge_asof(
        prices.sort_values("date"),
        valuation.sort_values("date"),
        on="date",
        direction="backward",
    )
    return prices


def valuation_wide(t):
    """Valuation measures (rows = measures, columns = dates) -> wide df (ticker, date, measures)."""
    v = t.get_valuation_measures().reset_index()
    if v is None or v.empty:
        return None
    v = v.rename(columns={"index": "measure", "Current": str(date.today())})
    long = v.melt(id_vars="measure", var_name="date", value_name="value")
    long["date"] = pd.to_datetime(long["date"], format="%m/%d/%Y", errors="coerce")
    long = long.dropna(subset=["date"])
    wide = long.pivot_table(index="date", columns="measure", values="value").reset_index()
    wide.columns.name = None
    return wide.rename(columns=VALUATION_RENAME)


def statement(df, fields):
    """yfinance statement (rows = items, columns = dates) -> one row per date."""
    out = pd.DataFrame({col: df.loc[label] for col, label in fields.items() if label in df.index})
    if out.empty:
        return None
    return out.rename_axis("date").reset_index()


def get_valuation(t):
    return valuation_wide(t)


TABLES = {
    "income_stmt": lambda t: statement(t.income_stmt, INCOME_FIELDS),
    "balance_sheet": lambda t: statement(t.balance_sheet, BALANCE_FIELDS),
    "cashflow": lambda t: statement(t.cashflow, CASHFLOW_FIELDS),
    "prices_weekly": get_prices,                               # history + valuation measures
    "earnings_estimate": lambda t: t.earnings_estimate.reset_index(),
    "revenue_estimate": lambda t: t.revenue_estimate.reset_index(),
    "eps_trend": lambda t: t.eps_trend.reset_index(),
    "eps_revisions": lambda t: t.eps_revisions.reset_index(),
    "company_info": get_info,                                  # ticker.info
}

# Analyst estimate tables are merged into one CSV at export time
ESTIMATE_SOURCES = ["earnings_estimate", "revenue_estimate", "eps_trend", "eps_revisions"]

if not hasattr(yf.Ticker, "get_valuation_measures"):
    print("WARNING: this yfinance version has no get_valuation_measures() - skipped. "
          "Try: pip install -U yfinance")


def rate_limited(e):
    return "ratelimit" in type(e).__name__.lower() or "too many requests" in str(e).lower()


# ------------------------------------------------------------------ fetch + export
def main():
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

    for name, parts in frames.items():
        if name in ESTIMATE_SOURCES:
            continue  # exported as analyst_estimates below

        if not parts:
            print(f"{name}: no data")
            continue
        df = pd.concat(parts, ignore_index=True)

        if name == "company_info":
            # merge info into the reference company list -> COMPANIES
            base = pd.read_csv(list_csv)[["ticker", "name", "sector", "industry"]]
            df = base.merge(df, on="ticker", how="left")
            df.to_csv(OUT / "companies.csv", index=False, encoding="utf-8-sig")
            print(f"companies: {len(df)} rows, {failures['company_info']} failed tickers -> {OUT / 'companies.csv'}")
            continue

        df.to_csv(OUT / f"{name}.csv", index=False, encoding="utf-8-sig")
        print(f"{name}: {len(df)} rows, {failures[name]} failed tickers -> {OUT / name}.csv")

    # analyst estimates: merge the 4 sources into one wide table (one row per ticker x period)
    merged = None
    for name in ESTIMATE_SOURCES:
        parts = frames[name]
        if not parts:
            continue
        df = pd.concat(parts, ignore_index=True).rename(columns=ESTIMATE_RENAMES[name])
        if name != "earnings_estimate":
            # currency/methodology are kept from earnings_estimate only
            df = df.drop(columns=["currency", "methodology"], errors="ignore")
        merged = df if merged is None else merged.merge(df, on=["ticker", "period"], how="outer")

    if merged is not None:
        merged.to_csv(OUT / "analyst_estimates.csv", index=False, encoding="utf-8-sig")
        print(f"analyst_estimates: {len(merged)} rows -> {OUT / 'analyst_estimates.csv'}")


if __name__ == "__main__":
    main()
