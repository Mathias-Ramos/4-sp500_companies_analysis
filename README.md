<div align="center">

🇫🇷 **[Version française](#version-française)** · 🇬🇧 **[English version](#english-version)**

</div>

---

<p align="center">
  <img src="https://img.shields.io/badge/Python-yfinance-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/AWS%20S3-Storage-569A31?logo=amazonaws&logoColor=white" alt="AWS S3">
  <img src="https://img.shields.io/badge/Snowflake-Data%20Warehouse-29B5E8?logo=snowflake&logoColor=white" alt="Snowflake">
  <img src="https://img.shields.io/badge/dbt-Data%20Transformation-FF694B?logo=dbt&logoColor=white" alt="dbt">
  <img src="https://img.shields.io/badge/Power%20BI-Visualization-F2C811?logo=powerbi&logoColor=black" alt="Power BI">
  <img src="https://img.shields.io/badge/Git%2FGitHub-181717?logo=github&logoColor=white" alt="Git/GitHub">
</p>

<div align="center">

🇫🇷 **Version française**

</div>

<a id="version-française"></a>

# 📈 S&P 500 : moteur de scoring d'investissement et analyse des entreprises

<p align="center">
  <strong>Transformer les données financières brutes en un score d'investissement fiable, comparable et exploitable — de l'extraction à l'aide à la décision.</strong>
</p>

## 🎯 Contexte & objectif

Évaluer ~500 entreprises cotées à la main n'est ni fiable ni reproductible : chaque investisseur regarde quelques ratios isolés, sans cadre de comparaison homogène au sein d'une même industrie.

Ce projet construit un **pipeline d'analytics engineering de bout en bout** qui :

- **Collecte** les données fondamentales, boursières et d'estimations analystes des ~500 sociétés du S&P 500.
- **Industrialise** les transformations avec dbt dans Snowflake, suivant une architecture en médaillon : nettoyage, KPIs normalisés par industrie, scoring.
- **Restitue** un **score d'investissement (0–100)** par entreprise, décliné par catégorie, via un tableau de bord Power BI interactif.

Objectif métier : répondre à *« où se situe cette entreprise par rapport à ses pairs, et sur quels leviers est-elle sous- ou sur-évaluée ? »*

## ⚡ Résultats clés

- **Scoring multi-facteurs** : chaque KPI est converti en score 0–100 par rang centile, puis agrégé avec des pondérations explicites (croissance, ROIC, dette, P/E, momentum technique).
- **Comparaison relative, pas absolue** : les P/E sont normalisés par la **médiane de l'industrie**, rendant les scores comparables entre secteurs dissemblables.
- **Vision instantanée par entreprise** : score global, rang dans l'industrie, détail des forces/faiblesses par catégorie, benchmark peers.
- **Reproductibilité complète** : de la collecte Python au dashboard, chaque étape est versionnée et rejouable.

| Capacité | Décision supportée |
|---|---|
| **Score d'investissement 0–100** | Cribler rapidement l'univers S&P 500 et prioriser les entreprises à analyser. |
| **Détail du score par catégorie** (P/E, ROIC, dette, croissance…) | Identifier précisément ce qui valorise ou pénalise une entreprise. |
| **P/E vs médiane de l'industrie** | Distinguer une entreprise chère d'une industrie intrinsèquement chère. |
| **Comparaison peers (ROIC vs EPS CAGR)** | Situer l'entreprise dans son écosystème concurrentiel. |
| **Tendance technique (SMA 50 semaines)** | Intégrer le momentum de marché à une analyse dominée par les fondamentaux. |

## 🧰 Stack technique

| Catégorie | Technologie | Rôle |
|---|---|---|
| Langage | **Python** (pandas, yfinance) | Collecte des données : scrape Wikipedia + API Yahoo Finance |
| Stockage brut | **AWS S3** | Zone de landing des fichiers CSV |
| Entrepôt de données | **Snowflake** | Environnement analytique (staging → transformations) |
| Transformation | **dbt** (Fusion) | Modélisation SQL, tests, documentation |
| BI / visualisation | **Power BI** | Tableau de bord interactif de scoring |
| Écosystème Python | **uv** | Gestion des dépendances et de l'environnement |
| Contrôle de version | **Git / GitHub** | Gestion du code source et documentation |

## 🏗️ Architecture du pipeline

```text
WIKIPEDIA (S&P 500)   YAHOO FINANCE API
        │                    │
        ▼                    ▼
┌─────────────────────────────────────┐
│ EXTRACT · Scripts Python            │
│ companies.csv + 7 jeux de données   │
│ (income, balance, cashflow, prices, │
│  metrics, EPS TTM, estimations)     │
└──────────────────┬──────────────────┘
                   ▼
┌─────────────────────────────────────┐
│ LOAD · AWS S3 → Snowflake STAGING   │
│ COPY INTO depuis un stage S3        │
└──────────────────┬──────────────────┘
                   ▼
┌─────────────────────────────────────┐
│ BRONZE · dbt staging : 8 modèles    │
│ Standardisation des données brutes  │
└──────────────────┬──────────────────┘
                   ▼
┌─────────────────────────────────────┐
│ SILVER · dbt intermediate : 3       │
│   - int_kpis    : ratios financiers │
│   - int_score   : scoring 0–100     │
│   - int_trend   : SMA 50 semaines    │
└──────────────────┬──────────────────┘
                   ▼
┌─────────────────────────────────────┐
│ GOLD · dbt marts : 4 modèles        │
│ score · score_detailed · peers ·    │
│ financials                          │
└──────────────────┬──────────────────┘
                   ▼
┌─────────────────────────────────────┐
│ POWER BI · Dashboard interactif     │
└─────────────────────────────────────┘
```

### Décomposition dbt (architecture en médaillon)

| Médaillon | Couche dbt | Modèles | Rôle |
|---|---|---|---|
| 🥉 Bronze | `staging` | **8** | Standardisation et typage des sources brutes Snowflake |
| 🥈 Silver | `intermediate` | **3** | Calcul des KPIs, normalisation par industrie, scoring, tendance |
| 🥇 Gold | `marts` | **4** | Agrégats de restitution pour Power BI |

## 🛠️ Approche analytique

1. **Extraire** : scraper la liste des constituants S&P 500 (Wikipedia), puis collecter via yfinance les états financiers, le bilan, les cash-flows, les prix quotidiens, les métriques de valorisation, l'EPS TTM et les estimations analystes.
2. **Charger** : déposer les CSV dans un bucket S3, puis les ingérer dans Snowflake (`COPY INTO` sur un stage S3, schéma `STAGING`).
3. **Transformer** (dbt) :
   - calculer les KPIs par entreprise : P/E trailing & forward, Net Debt / EBITDA, ROIC *(NOPAT / capital investi)*, FCF / Net Income, EPS CAGR 3 ans ;
   - construire un **trend score** technique : position vs moyenne mobile 50 semaines, bonus bullish, pénalité par clôture baissière consécutive, bonus de proximité à la SMA ;
   - scorer chaque KPI de 0 à 100 via `PERCENT_RANK()`, en normalisant les P/E par la médiane de l'industrie avant scoring.
4. **Agréger** : combiner les scores par catégorie avec des pondérations fixes en un score d'investissement global.
5. **Restituer** : alimenter un dashboard Power BI orienté décision.

### 🧮 Méthodologie de scoring

Chaque catégorie est un rang centile sur l'univers S&P 500 (100 = meilleur), les valeurs manquantes étant pénalisées :

| Catégorie | KPI normalisé | Pondération |
|---|---|---|
| P/E | Trailing P/E et Forward P/E relatifs à la médiane de l'industrie | 8 % + 8 % |
| Momentum | Trend score technique (SMA 50 semaines) | 14 % |
| Net debt | Net Debt / EBITDA | 14 % |
| ROIC | NOPAT / Capital investi | 14 % |
| Earnings | FCF / Net Income (qualité des bénéfices) | 14 % |
| Growth | EPS CAGR 3 ans | 14 % |

Le score final est la combinaison pondérée :

**score = 0.08·PE_trailing + 0.08·PE_forward + 0.14·(trend + net_debt + roic + earnings + growth)**, borné à 0–100.

*(pondérations ajustables dans `int_score.sql` ; les comparaisons de P/E sont relatives à l'industrie, pas en valeur absolue.)*

## 📊 Tableau de bord Power BI

Le dashboard permet l'analyse d'une entreprise à la fois, dans son contexte d'industrie :

| # | Visuel | Contenu |
|---|---|---|
| 1 | **Slicers** (Sector, Industry, Ticker) | Filtre global de la page ; sélection d'un ticker pour focaliser l'analyse |
| 2 | **Carte** | Nom de l'entreprise sélectionnée |
| 3 | **Jauge** | Score d'investissement global (0–100) |
| 4 | **Carte KPI** | Rang de l'entreprise dans son industrie |
| 5 | **Carte KPI + référence** | Trailing P/E et écart relatif vs médiane de l'industrie |
| 6 | **Combo chart** | Net margin et Revenue par exercice : croissance accompagnée ou non de rentabilité |
| 7 | **Barres horizontales** | Score détaillé par catégorie : forces et faiblesses |
| 8 | **Nuage de points** | ROIC vs EPS CAGR (3Y) des pairs, taille = Free Cash Flow |
| 9 | **Table** | Comparaison du score avec les concurrents + moyenne des pairs |

Lecture type : une entreprise au **ROIC élevé et à l'EPS CAGR soutenue** se positionne en haut à droite du nuage de pairs — une combinaison rare et valorisée ; un **score global moyen mais une catégorie « Growth » élevée** invite à creuser le potentiel spécifique.

## 📁 Structure du répertoire

```text
4-sp500_companies_analysis/
│
├── scripts/
│   ├── get_companies.py            # Scrape la liste S&P 500 (Wikipedia)
│   └── financial_data.py           # Collecte yfinance → CSV dans data/raw/
│
├── data/
│   ├── raw/                        # CSV bruts (landing zone locale)
│   └── processed/
│
├── ddl/
│   ├── ddl.sql                     # Création des tables Snowflake (STAGING)
│   └── resources.sql               # Stage S3, file format, COPY INTO
│
├── analytics/                      # Projet dbt
│   ├── models/
│   │   ├── staging/                # 8 modèles : sources standardisées
│   │   ├── intermediate/           # 3 modèles : KPIs, scoring, tendance
│   │   └── marts/                  # 4 modèles : restitution Power BI
│   ├── dbt_project.yml
│   └── sources.yml
│
├── docs/
│   └── powerbi_dashboard.md        # Spécification du dashboard Power BI
│
├── pyproject.toml                  # Python 3.14, uv, pandas, yfinance, dbt
├── .env.example
└── README.md
```

## ⚙️ Pour reproduire le projet

```bash
# 1. Environnement Python
uv sync

# 2. Collecte des données
python scripts/get_companies.py
python scripts/financial_data.py

# 3. Chargement S3 → Snowflake (identifiants AWS dans .env)
#    Exécuter ddl/resources.sql puis ddl/ddl.sql

# 4. Transformations dbt
cd analytics && dbt build

# 5. Dashboard : connecter Power BI aux marts Snowflake
```

## ⚠️ Limites & prochaines étapes

- **Fraîcheur des données** : les sources yfinance fournissent des historiques annuels ; les KPIs reflètent le dernier exercice connu. Ajouter des tests de fraîcheur dbt (déjà amorcés sur `balance_sheet`) pour toutes les sources.
- **Tests & qualité** : étendre les tests dbt (unicité des tickers, valeurs non négatives, nulls critiques) et les prédicats sur le scoring.
- **Scoring** : faire évoluer les pondérations fixes vers une calibration backtestée, et étudier l'ajout de facteurs qualitatifs.
- **Orchestration** : industrialiser la chaîne complète (collecte → load → dbt → refresh Power BI) avec un scheduler.
- **Distribution** : version web du dashboard (Power BI Service) et exports d'alertes (entrées/sorties de Top N par industrie).

## 👋 À propos de moi

**Analytics Engineer** — je conçois des pipelines de données fiables et des modèles analytiques qui transforment des données brutes en décisions.

Vous pouvez retrouver d'autres projets dans mon **[Portfolio](https://github.com/nicolas-martin)**.

<p>
  <a href="https://www.linkedin.com/in/nicolas-martin">LinkedIn</a> •
  <a href="mailto:contact@example.com">Email</a>
</p>

---

<div align="center">

🇬🇧 **English version**

</div>

<a id="english-version"></a>

# 📈 S&P 500: Investment Scoring Engine & Company Analysis

<p align="center">
  <strong>Turning raw financial data into a reliable, comparable and actionable investment score — from extraction to decision support.</strong>
</p>

## 🎯 Context & objective

Manually assessing ~500 publicly listed companies is neither reliable nor reproducible: most investors look at a handful of isolated ratios, with no homogeneous comparison framework within the same industry.

This project builds an **end-to-end analytics engineering pipeline** that:

- **Collects** fundamentals, market prices and analyst estimates for the ~500 S&P 500 constituents.
- **Industrializes** transformations with dbt in Snowflake, following a medallion architecture: cleaning, industry-normalized KPIs, scoring.
- **Delivers** a **0–100 investment score** per company, broken down by category, through an interactive Power BI dashboard.

Business goal: answer *"where does this company stand versus its peers, and on which levers is it under- or over-valued?"*

## ⚡ Key results

- **Multi-factor scoring**: each KPI is converted into a 0–100 score using percentile ranking, then aggregated with explicit weights (growth, ROIC, debt, P/E, technical momentum).
- **Relative, not absolute comparison**: P/E ratios are normalized against the **industry median**, making scores comparable across dissimilar sectors.
- **One-company snapshot**: overall score, industry rank, category-level strengths/weaknesses, peer benchmark.
- **Full reproducibility**: from Python collection to dashboard, every step is versioned and replayable.

| Capability | Supported decision |
|---|---|
| **0–100 investment score** | Quickly screen the S&P 500 universe and prioritize companies for deeper analysis. |
| **Score breakdown by category** (P/E, ROIC, debt, growth…) | Pinpoint exactly what drives or drags a company's valuation. |
| **P/E vs industry median** | Distinguish an expensive company from an intrinsically expensive industry. |
| **Peer comparison (ROIC vs EPS CAGR)** | Position the company within its competitive landscape. |
| **Technical trend (50-week SMA)** | Factor market momentum into an analysis otherwise dominated by fundamentals. |

## 🧰 Tech stack

| Category | Technology | Role |
|---|---|---|
| Language | **Python** (pandas, yfinance) | Data collection: Wikipedia scrape + Yahoo Finance API |
| Raw storage | **AWS S3** | CSV landing zone |
| Data warehouse | **Snowflake** | Analytical environment (staging → transformations) |
| Transformation | **dbt** (Fusion) | SQL modeling, tests, documentation |
| BI / visualization | **Power BI** | Interactive scoring dashboard |
| Python tooling | **uv** | Dependency and environment management |
| Version control | **Git / GitHub** | Source control and project documentation |

## 🏗️ Pipeline architecture

```text
WIKIPEDIA (S&P 500)   YAHOO FINANCE API
        │                    │
        ▼                    ▼
┌─────────────────────────────────────┐
│ EXTRACT · Python scripts            │
│ companies.csv + 7 datasets          │
│ (income, balance, cashflow, prices, │
│  metrics, TTM EPS, estimates)       │
└──────────────────┬──────────────────┘
                   ▼
┌─────────────────────────────────────┐
│ LOAD · AWS S3 → Snowflake STAGING   │
│ COPY INTO from an S3 stage          │
└──────────────────┬──────────────────┘
                   ▼
┌─────────────────────────────────────┐
│ BRONZE · dbt staging: 8 models      │
│ Standardization of raw data         │
└──────────────────┬──────────────────┘
                   ▼
┌─────────────────────────────────────┐
│ SILVER · dbt intermediate: 3 models │
│   - int_kpis    : financial ratios  │
│   - int_score   : 0–100 scoring     │
│   - int_trend   : 50-week SMA trend  │
└──────────────────┬──────────────────┘
                   ▼
┌─────────────────────────────────────┐
│ GOLD · dbt marts: 4 models          │
│ score · score_detailed · peers ·    │
│ financials                          │
└──────────────────┬──────────────────┘
                   ▼
┌─────────────────────────────────────┐
│ POWER BI · Interactive dashboard    │
└─────────────────────────────────────┘
```

### dbt breakdown (medallion architecture)

| Medallion layer | dbt layer | Models | Role |
|---|---|---|---|
| 🥉 Bronze | `staging` | **8** | Standardization and typing of raw Snowflake sources |
| 🥈 Silver | `intermediate` | **3** | KPI calculation, industry normalization, scoring, trend |
| 🥇 Gold | `marts` | **4** | Reporting aggregates for Power BI |

## 🛠️ Analytical approach

1. **Extract**: scrape the S&P 500 constituents list (Wikipedia), then collect via yfinance the income statements, balance sheets, cash flows, daily prices, valuation metrics, TTM EPS and analyst estimates.
2. **Load**: push the CSVs to an S3 bucket, then ingest into Snowflake (`COPY INTO` from an S3 stage, `STAGING` schema).
3. **Transform** (dbt):
   - compute company-level KPIs: trailing & forward P/E, Net Debt / EBITDA, ROIC *(NOPAT / invested capital)*, FCF / Net Income, 3-year EPS CAGR;
   - build a technical **trend score**: position vs the 50-week moving average, bullish bonus, penalty per consecutive bearish close, proximity-to-SMA bonus;
   - score each KPI 0–100 with `PERCENT_RANK()`, normalizing P/Es against the industry median before scoring.
4. **Aggregate**: combine category scores with fixed weights into a single investment score.
5. **Deliver**: feed a decision-oriented Power BI dashboard.

### 🧮 Scoring methodology

Each category is a percentile rank across the S&P 500 universe (100 = best), with missing values penalized:

| Category | Normalized KPI | Weight |
|---|---|---|
| P/E | Trailing and forward P/E relative to the industry median | 8% + 8% |
| Momentum | Technical trend score (50-week SMA) | 14% |
| Net debt | Net Debt / EBITDA | 14% |
| ROIC | NOPAT / Invested capital | 14% |
| Earnings | FCF / Net Income (earnings quality) | 14% |
| Growth | 3-year EPS CAGR | 14% |

The final score is the weighted combination:

**score = 0.08·PE_trailing + 0.08·PE_forward + 0.14·(trend + net_debt + roic + earnings + growth)**, bounded 0–100.

*(weights are adjustable in `int_score.sql`; P/E comparisons are relative to the industry, not absolute.)*

## 📊 Power BI dashboard

The dashboard analyzes one company at a time, within its industry context:

| # | Visual | Content |
|---|---|---|
| 1 | **Slicers** (Sector, Industry, Ticker) | Page-wide filter; select a ticker to focus the analysis |
| 2 | **Card** | Selected company name |
| 3 | **Gauge** | Overall investment score (0–100) |
| 4 | **KPI card** | Company rank within its industry |
| 5 | **KPI card + reference label** | Trailing P/E and relative gap vs industry median |
| 6 | **Combo chart** | Net margin and Revenue by fiscal year: growth with or without profitability |
| 7 | **Horizontal bars** | Score breakdown by category: strengths and weaknesses |
| 8 | **Scatter plot** | Peers' ROIC vs EPS CAGR (3Y), bubble size = Free Cash Flow |
| 9 | **Table** | Score comparison against competitors + peer average |

Typical read: a company with **high ROIC and sustained EPS CAGR** sits in the top-right of the peer scatter — a rare and rewarded combination; an **average overall score but a high "Growth" category** invites digging into company-specific potential.

## 📁 Repository structure

```text
4-sp500_companies_analysis/
│
├── scripts/
│   ├── get_companies.py            # Scrape the S&P 500 list (Wikipedia)
│   └── financial_data.py           # yfinance collection → CSV in data/raw/
│
├── data/
│   ├── raw/                        # Raw CSVs (local landing zone)
│   └── processed/
│
├── ddl/
│   ├── ddl.sql                     # Snowflake table creation (STAGING)
│   └── resources.sql               # S3 stage, file format, COPY INTO
│
├── analytics/                      # dbt project
│   ├── models/
│   │   ├── staging/                # 8 models: standardized sources
│   │   ├── intermediate/           # 3 models: KPIs, scoring, trend
│   │   └── marts/                  # 4 models: Power BI reporting
│   ├── dbt_project.yml
│   └── sources.yml
│
├── docs/
│   └── powerbi_dashboard.md        # Power BI dashboard specification
│
├── pyproject.toml                  # Python 3.14, uv, pandas, yfinance, dbt
├── .env.example
└── README.md
```

## ⚙️ Reproducing the project

```bash
# 1. Python environment
uv sync

# 2. Data collection
python scripts/get_companies.py
python scripts/financial_data.py

# 3. S3 → Snowflake loading (credentials in .env)
#    Run ddl/resources.sql then ddl/ddl.sql

# 4. dbt transformations
cd analytics && dbt build

# 5. Dashboard: connect Power BI to the Snowflake marts
```

## ⚠️ Limitations & next steps

- **Data freshness**: yfinance sources provide annual histories; KPIs reflect the latest known fiscal year. Extend dbt freshness tests (already seeded on `balance_sheet`) to all sources.
- **Tests & quality**: expand dbt tests (ticker uniqueness, non-negative values, critical nulls) and scoring constraints.
- **Scoring**: move from fixed weights to backtested calibration, and study adding qualitative factors.
- **Orchestration**: productionize the full chain (collect → load → dbt → Power BI refresh) with a scheduler.
- **Distribution**: web version of the dashboard (Power BI Service) and alert exports (industry Top N entries/exits).

## 👋 About me

**Analytics Engineer** — I design reliable data pipelines and analytical models that turn raw data into decisions.

More projects are available in my **[Portfolio](https://github.com/nicolas-martin)**.

<p>
  <a href="https://www.linkedin.com/in/nicolas-martin">LinkedIn</a> •
  <a href="mailto:contact@example.com">Email</a>
</p>
