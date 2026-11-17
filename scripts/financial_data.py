# Fetch yfinance data -> one CSV per dataset in data/raw/ (one row per ticker x date/period)
import time
from datetime import date
from pathlib import Path

import pandas as pd
import yfinance as yf

OUT = Path("data/raw")
companies = pd.read_csv(OUT / "companies.csv")  # created by companies.py
symbols = companies["ticker"].dropna().unique().tolist()

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

# analyst estimates: yfinance table -> {yfinance column: output column}
ESTIMATE_RENAMES = {
    "earnings_estimate": {
        "avg": "eps_avg", "low": "eps_low", "high": "eps_high",
        "yearAgoEps": "eps_year_ago", "numberOfAnalysts": "eps_number_of_analysts",
        "growth": "eps_growth",
    },
    "revenue_estimate": {
        "avg": "revenue_avg", "low": "revenue_low", "high": "revenue_high",
        "numberOfAnalysts": "revenue_number_of_analysts",
        "yearAgoRevenue": "revenue_year_ago", "growth": "revenue_growth",
    },
    "eps_trend": {
        "current": "trend_current", "7daysAgo": "trend_7_days_ago",
        "30daysAgo": "trend_30_days_ago", "60daysAgo": "trend_60_days_ago",
        "90daysAgo": "trend_90_days_ago",
    },
    "eps_revisions": {
        "upLast7days": "up_last_7_days", "upLast30days": "up_last_30_days",
        "downLast30days": "down_last_30_days", "downLast7Days": "down_last_7_days",
    },
}


# ------------------------------------------------------------------ one function per dataset
def statement(df, fields):
    """Statement (rows = items, columns = dates) -> one row per date.

    Yahoo sometimes returns the oldest fiscal-year column present but entirely
    empty; such rows are dropped so they never pollute the raw data.
    """
    out = pd.DataFrame({col: df.loc[label] for col, label in fields.items() if label in df.index})
    out = out.dropna(how="all")
    return out.rename_axis("date").reset_index()


def get_ttm_eps(t):
    """Trailing-twelve-month diluted EPS = rolling sum of the last 4 quarters."""
    eps = t.quarterly_income_stmt.loc["Diluted EPS"].dropna().sort_index()
    ttm = eps.rolling(4).sum().dropna()
    return ttm.rename("ttm_eps").rename_axis("date").reset_index()


def get_prices(t):
    """Daily closing prices, last 20 years."""
    start = (pd.Timestamp.today() - pd.DateOffset(years=20)).strftime("%Y-%m-%d")
    h = t.history(start=start, interval="1d", auto_adjust=True)
    prices = h[["Close"]].rename(columns={"Close": "rounded_close"}).round(2)
    prices.index = prices.index.tz_localize(None)
    return prices.rename_axis("date").reset_index()


def get_metrics(t):
    """Valuation measures (rows = measures, columns = dates) -> one row per date."""
    v = t.get_valuation_measures().reset_index()
    v = v.rename(columns={"index": "measure", "Current": str(date.today())})
    long = v.melt(id_vars="measure", var_name="date", value_name="value")
    long["date"] = pd.to_datetime(long["date"], format="%m/%d/%Y", errors="coerce")
    wide = long.dropna(subset=["date"]).pivot_table(
        index="date", columns="measure", values="value"
    ).reset_index()
    wide.columns.name = None
    return wide.rename(columns=VALUATION_RENAME)


def get_estimates(t):
    """The 4 analyst estimate tables merged into one row per period."""
    merged = None
    for name, rename in ESTIMATE_RENAMES.items():
        df = getattr(t, name).reset_index().rename(columns=rename)
        if merged is None:
            merged = df
        else:  # currency/methodology are kept from earnings_estimate only
            df = df.drop(columns=["currency", "methodology"], errors="ignore")
            merged = merged.merge(df, on="period", how="outer")
    return merged


def get_info(t):
    info = t.info
    return pd.DataFrame([{"country": info.get("country"), "currency": info.get("currency")}])


TABLES = {
    "income_stmt": lambda t: statement(t.income_stmt, INCOME_FIELDS),
    "balance_sheet": lambda t: statement(t.balance_sheet, BALANCE_FIELDS),
    "cashflow": lambda t: statement(t.cashflow, CASHFLOW_FIELDS),
    "ttm_eps": get_ttm_eps,
    "prices_daily": get_prices,
    "metrics": get_metrics,
    "analyst_estimates": get_estimates,
    "company_info": get_info,
}


# ------------------------------------------------------------------ fetch + export
def main():
    frames = {name: [] for name in TABLES}
    failures = dict.fromkeys(TABLES, 0)
    rate_limited = False

    for i, sym in enumerate(symbols, 1):
        t = yf.Ticker(sym)
        for name, fetch in TABLES.items():
            try:
                df = fetch(t)
                if df is not None and not df.empty:
                    df.insert(0, "ticker", sym)
                    frames[name].append(df)
            except Exception as e:
                if "too many requests" in str(e).lower() or "ratelimit" in type(e).__name__.lower():
                    rate_limited = True
                    break
                failures[name] += 1
        if rate_limited:
            print(f"Rate limited at {sym} - stopping, saving what we have.")
            break
        print(f"[{i}/{len(symbols)}] {sym}")
        time.sleep(0.1)

    for name, parts in frames.items():
        if not parts:
            print(f"{name}: no data")
            continue
        df = pd.concat(parts, ignore_index=True)
        path = OUT / f"{name}.csv"
        if name == "company_info":  # merge into the company list -> companies.csv
            df = companies[["ticker", "name", "sector", "industry"]].merge(df, on="ticker", how="left")
            path = OUT / "companies.csv"
        df.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"{name}: {len(df)} rows, {failures[name]} failed tickers -> {path}")


if __name__ == "__main__":
    main()