![Job Intelligence Dashboard](assets/portfolio_screenshot.png)

# LinkedIn Job Intelligence System 🎯

**Automated VP/Director-level job scraping and enrichment pipeline for SaaS companies**

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Playwright](https://img.shields.io/badge/Playwright-1.48-green)
![Status](https://img.shields.io/badge/Status-Production-success)

---

## 📊 What It Does

Extracts and enriches VP/Director/CTO job postings from LinkedIn with:
- ✅ Company data (size, revenue, industry)
- ✅ Tech stack analysis (Python, AWS, React, etc.)
- ✅ Professional Excel + JSON exports
- ✅ Intelligence report generation

**Sample Output:** 39 clean jobs in 15 minutes

---

## 🚀 Features

- **Stealth Scraping:** Bypasses LinkedIn anti-bot detection
- **Data Enrichment:** Auto-extracts company info + tech stacks
- **Quality Filtering:** Removes incomplete/masked data
- **Professional Reports:** Excel + PDF deliverables
- **Production-Ready:** Error handling, rate limiting, deduplication

---

## 🛠️ Tech Stack

- **Scraping:** Playwright (async), headless browser automation
- **Data Processing:** Pandas, Polars, JSON
- **Export Formats:** Excel (openpyxl), PDF (markdown conversion)
- **Language:** Python 3.11+
- **Deployment:** Windows/Linux compatible

---

## 📈 Sample Results


---

## 🎯 Use Cases

1. **Recruiters:** Fresh VP+ leads for outbound recruitment
2. **Sales Teams:** Target fast-growing companies actively hiring
3. **Job Seekers:** Find senior roles with tech stack filtering
4. **Market Research:** Track hiring trends in SaaS sector

---

## 📦 Deliverable Package

Each run produces:
- `SaaS_Jobs_CLEAN_FINAL.xlsx` - Main dataset (sortable, filterable)
- `SaaS_Jobs_CLEAN_FINAL.json` - Machine-readable format
- `Intelligence_Report.pdf` - Executive summary with insights
- `README.txt` - Usage instructions

---

## ⚡ Quick Start

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/linkedin-job-scraper.git
cd linkedin-job-scraper

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run scraper
python main.py

# Generate enriched deliverable
python enrichment.py
python add_manual_data.py
python filter_clean_jobs.py
python generate_report.py