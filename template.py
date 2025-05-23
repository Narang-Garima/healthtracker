import os

folders = [
    "data",
    "notebooks",
    "dashboard",
    "analysis",
    ".github/workflows"
]

files = {
    "README.md": """# Pediatric Health Tracker 🚼

Tracks pediatric ER wait times and weekly RSV outbreaks for analysis, forecasting, and visualization.

## Project Phases
1. **Data Collection** – via web scraping from LHSC and CDC
2. **Data Understanding** – exploratory notebooks
3. **Visualization** – Jupyter / Streamlit
4. **Analysis** – Time-series trends, correlations, forecasting

""",

    "requirements.txt": "requests\nbeautifulsoup4\npandas\n",

    "scrape_and_merge.py": "# This will contain your scraper for ER wait times + CDC RSV data\n",

    "notebooks/01_data_exploration.ipynb": "",

    "dashboard/app.py": "# Optional: Streamlit app goes here\n",

    "analysis/forecast_model.py": "# Future prediction model (e.g., forecasting ER wait times from RSV trends)\n",

    ".github/workflows/scraper.yml": """name: Run Scraper Hourly

on:
  schedule:
    - cron: '0 * * * *'
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run scraper
        run: python scrape_and_merge.py

      - name: Commit updated data
        run: |
          git config --global user.email "actions@github.com"
          git config --global user.name "github-actions"
          git add data/*.csv
          git commit -m "Auto-update: ER wait & RSV data" || echo "No changes"
          git push
"""
}

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Create files with content
for filepath, content in files.items():
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print(" Project folder structure created successfully.")
