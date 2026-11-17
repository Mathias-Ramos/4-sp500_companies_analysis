# Power BI Dashboard Recap: Company Investment Score

## Overview

| # | Visual type | Title | Position |
|---|---|---|---|
| 1 | Dropdown slicers (x3) | "Choose your settings" | Top left |
| 2 | Text box / card | Company name | Top center |
| 3 | Gauge | Investment Score | Top, 2nd block |
| 4 | Card (KPI) | Industry rank | Top, 3rd block |
| 5 | Card (KPI) with reference label | Trailing P/E | Top, 4th block |
| 6 | Combo chart (clustered columns + line) | Net margin and Revenue by Year | Top right |
| 7 | Horizontal bar chart | Investment score detailed by category | Bottom left |
| 8 | Scatter / bubble chart | ROIC vs. EPS CAGR | Bottom center |
| 9 | Table | Competitors score | Bottom right |

---

## Details by visual

### 1. Slicers: "Choose your settings"
- **Type:** Three dropdown slicers
- **Fields:** `SECTOR`, `INDUSTRY`, `TICKER`
- **Role:** Filter the whole page. Select a single ticker to analyze one company.

### 2. Company name
- **Type:** Card or dynamic title
- **Data:** Name of the selected company

### 3. Investment Score
- **Type:** Gauge
- **Data:** Global investment score of the selected company (`mart_score[score]`)
- **Reading:** Score on a 0 to 100 scale, where 100 is best.

### 4. Industry rank
- **Type:** Single-value card
- **Data:** The company's rank within its industry, based on the investment score

### 5. Trailing P/E
- **Type:** New card visual with a reference label
- **Value:** `Avg Trailing PE`, the company's trailing P/E, formatted `0.0"x"`
- **Reference label:** `PE vs Industry %`, the relative gap to the industry median, formatted `+0%;-0%` and titled "vs industry median"
- **Source columns:** `mart_score[trailing_pe]` and `mart_score[avg_industry_trail_pe]`. The industry value is a median (`PERCENTILE_CONT(0.5)` in `int_kpis`).
- **Reading:** A positive gap means the stock is more expensive than its industry. A negative gap means it trades at a discount.

### 6. Net margin and Revenue by Year
- **Type:** Combo chart (clustered columns and line)
- **X-axis:** Fiscal year
- **Columns:** Net margin (left axis)
- **Line:** Revenue (right axis)
- **Reading:** Shows whether revenue growth comes with stable, improving or shrinking profitability.

### 7. Investment score detailed by category
- **Type:** Horizontal bar chart, sorted in descending order
- **Y-axis:** Category. **X-axis:** Score (0 to 100)
- **Data labels:** Shown at the end of each bar
- **Source:** `mart_score_detailed` (`score_cat`, `score`)
- **Categories:** Technical, Growth, P/E, Earnings, Net debt, ROIC, General (overall score)
- **Reading:** Highlights the company's strengths and the categories that drag the overall score down.

### 8. ROIC vs. EPS CAGR
- **Type:** Scatter / bubble chart
- **X-axis:** ROIC. **Y-axis:** EPS CAGR (3Y)
- **Bubbles:** Each bubble is a peer company. Size represents Free Cash Flow.
- **Tooltip:** Peer name, ROIC, EPS CAGR (3Y), Free Cash Flow, Industry
- **Reading:** Peers in the top right combine high returns on capital with strong earnings growth. Outliers can distort the axes.

### 9. Competitors score
- **Type:** Table with scrollbar, sorted ascending by Score
- **Columns:** Industry, Ticker, Score
- **Total row:** Average score of the displayed peers
- **Reading:** Compares the selected company's score with the peer average.