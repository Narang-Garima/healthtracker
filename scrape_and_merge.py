# This will contain your scraper for ER wait times + CDC RSV data
import requests
import datetime
import pathlib
import pandas as pd
from bs4 import BeautifulSoup

DATA_DIR = pathlib.Path("data")
DATA_DIR.mkdir(exist_ok=True)

# ER wait time scraper
def fetch_lhsc_wait():
    url = "https://www.lhsc.on.ca/emergency-department/childrens-hospital-emergency-department-wait-times"
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    header = soup.find("h3", string=lambda s: s and "Current wait time" in s)
    wait_h1 = header.find_next("h1") if header else None
    hours_text = wait_h1.text.strip() if wait_h1 else None
    wait_hours = float(hours_text.split()[0]) if hours_text else None

    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    return {"timestamp": timestamp, "hospital": "LHSC_CHILDRENS", "wait_hours": wait_hours}

# RSV weekly download + clean
def fetch_rsv_weekly():
    csv_url = "https://data.cdc.gov/api/views/3cxc-4k8q/rows.csv?accessType=DOWNLOAD"
    df = pd.read_csv(csv_url)

    # Fix column name if needed
    if 'week_end' not in df.columns:
        for col in df.columns:
            if 'week' in col and 'end' in col:
                df.rename(columns={col: 'week_end'}, inplace=True)
                break

    if 'week_end' in df.columns:
        df['week_end'] = pd.to_datetime(df['week_end'], format="%Y-%m-%d", errors='coerce')

    df["downloaded_at"] = pd.Timestamp.utcnow()

    if "region_type" in df.columns and "region" in df.columns:
        df = df[df["region_type"] == "National"]
        if {"week_end", "region", "percent_positive"}.issubset(df.columns):
            df = df[["week_end", "region", "percent_positive", "downloaded_at"]]

    return df

# Append to CSVs
def main():
    try:
        er_row = fetch_lhsc_wait()
        er_file = DATA_DIR / "er_wait_times.csv"
        pd.DataFrame([er_row]).to_csv(
            er_file, mode="a", header=not er_file.exists(), index=False
        )
        print("✅ ER wait time saved.")
    except Exception as e:
        print(f"❌ Error fetching ER wait time: {e}")

    try:
        rsv_df = fetch_rsv_weekly()
        rsv_file = DATA_DIR / "rsv_weekly.csv"
        if rsv_file.exists():
            existing = pd.read_csv(rsv_file, parse_dates=["week_end"])
            rsv_df = rsv_df[~rsv_df["week_end"].isin(existing["week_end"])]
        rsv_df.to_csv(rsv_file, mode="a", header=not rsv_file.exists(), index=False)
        print("✅ RSV weekly data updated.")
    except Exception as e:
        print(f"❌ Error fetching RSV data: {e}")

if __name__ == "__main__":
    main()
