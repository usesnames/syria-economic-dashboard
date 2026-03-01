# Syria Economic Dashboard

A single-page interactive dashboard tracking Syria's economic indicators — consumer prices, wages, GDP, population dynamics, and the refugee crisis.

**[Live Dashboard →](https://usesnames.github.io/syria-economic-dashboard/)**

---

## Overview

The dashboard aggregates data from multiple sources into five thematic tabs:

| Tab | Source | Data |
|-----|--------|------|
| **CPI** | [SCPR](https://scpr-syria.org/publications/bulletins/) | Consumer Price Index by governorate and commodity (base year 2021=100) |
| **Wages** | SCPR | Average monthly wages by control area (GoS, TL, AA) and sector |
| **Economy** | [World Bank API](https://api.worldbank.org/v2/) | GDP, GDP per capita, GDP growth, with constant/current USD toggle |
| **Population & Conflict** | World Bank API | Total population, life expectancy, refugee population |
| **Refugees** | [UNHCR API](https://data.unhcr.org/) | Refugees by country, resettlement, returns, demographics |

## Architecture

```
index.html          ← Self-contained dashboard (HTML + CSS + JS, no build step)
data/
  cpi_data.json     ← SCPR CPI & wage data (auto-updated weekly)
scripts/
  update_data.py    ← Standalone scraping pipeline
  requirements.txt  ← Python dependencies for CI
.github/workflows/
  update-data.yml   ← GitHub Actions weekly cron job
```

The dashboard is a **single static HTML file** served via GitHub Pages. CPI/wage data is loaded from a committed JSON file; World Bank and UNHCR data is fetched client-side from public APIs at runtime.

## Data Pipeline

The SCPR data pipeline (`scripts/update_data.py`) performs the following steps:

1. **Scrape** the SCPR bulletins page for new English-language PDF links
2. **Download** any new bulletins (cached between runs)
3. **Extract CPI** from appendix tables in each PDF (all commodities × 14 governorates + national)
4. **Back-calculate** missing months using month-on-month inflation tables
5. **Gap-fill** from chart data labels where table extraction fails
6. **Extract wages** from wage tables (public/private/civil sectors × control areas)
7. **Export** `data/cpi_data.json`

A **GitHub Actions workflow** runs this pipeline every Monday at 06:00 UTC. If new data is found, the bot auto-commits to `main` and GitHub Pages redeploys.

## Local Development

```bash
# Serve locally (any static server works)
python -m http.server 8000

# Run the data update script manually
pip install -r scripts/requirements.txt
python scripts/update_data.py
```

## Tech Stack

- **Frontend**: Vanilla HTML/CSS/JS, [Plotly.js](https://plotly.com/javascript/) for charts
- **Data extraction**: Python, [pdfplumber](https://github.com/jsvine/pdfplumber), BeautifulSoup
- **Hosting**: GitHub Pages
- **CI/CD**: GitHub Actions (weekly cron)
- **APIs**: World Bank Data API v2, UNHCR Population Data API

## Development Process

This project was developed extensively with **Claude Opus** (Anthropic) via GitHub Copilot in VS Code. Claude assisted with:

- Dashboard design and full frontend implementation (HTML, CSS, responsive layout, dark mode)
- Plotly.js chart configuration and interactivity
- PDF scraping pipeline — CPI table extraction, wage parsing, gap-filling strategies
- World Bank and UNHCR API integration (endpoint discovery, data path debugging, CORS testing)
- GitHub Actions workflow for automated weekly data updates
- Iterative bug fixing, code refactoring, and deployment

The entire codebase — from the initial notebook prototype to the production dashboard and CI pipeline — was built through an interactive conversation with Claude Opus over multiple sessions.

## License

MIT
