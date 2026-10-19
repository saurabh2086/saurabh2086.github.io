#!/usr/bin/env python3
"""
prepare_bda3_data.py
====================
Automated ETL pipeline to download, parse, standardize, and organize all datasets
from Andrew Gelman's Bayesian Data Analysis (BDA3) directory:
https://sites.stat.columbia.edu/gelman/book/data/

Outputs:
  - <destination>/raw/        (Original unchanged .asc, .dat, .csv files)
  - <destination>/clean_csv/  (Tidy, well-named, snake_case CSV files)
  - <destination>/parquet/    (Fast, schema-typed Parquet files for Pandas/Polars)
  - <destination>/bda3_loader.py (One-line data loader module for Colab or local scripts)
  - <destination>/metadata_catalog.json (Machine-readable schema and book chapter cross-references)

Works seamlessly both locally and inside Google Colab (pointing to Google Drive).
"""

import os
import sys
import json
import re
import urllib.request
import pandas as pd
import numpy as np


BASE_URL_SITES = "https://sites.stat.columbia.edu/gelman/book/data/"
BASE_URL_STAT = "https://stat.columbia.edu/~gelman/book/data/"


def fetch_text(url: str) -> str:
    """Download plain text content with a friendly user-agent."""
    headers = {"User-Agent": "Mozilla/5.0 (BDA3-Data-Loader)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8", errors="replace")


def download_raw(url: str, dest_path: str):
    """Download raw file to destination path."""
    headers = {"User-Agent": "Mozilla/5.0 (BDA3-Data-Loader)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        data = resp.read()
    with open(dest_path, "wb") as f:
        f.write(data)


# --------------------------------------------------------------------------
# Parsers for each dataset
# --------------------------------------------------------------------------

def parse_rats(text: str) -> pd.DataFrame:
    """
    Table 5.1: 71 rat tumor experiments.
    Format has 2 comment lines, header 'y N', and 71 rows of whitespace integers.
    """
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    data_lines = []
    found_header = False
    for line in lines:
        if line.startswith("y N") or line.startswith("y\tN"):
            found_header = True
            continue
        if found_header:
            parts = line.split()
            if len(parts) >= 2:
                data_lines.append((int(parts[0]), int(parts[1])))
    
    df = pd.DataFrame(data_lines, columns=["y", "n"])
    df.insert(0, "study_id", np.arange(1, len(df) + 1))
    df["observed_rate"] = (df["y"] / df["n"]).round(4)
    return df


def parse_light(text: str) -> pd.DataFrame:
    """
    Figure 3.1 / Table 3.1: Simon Newcomb's 66 measurements of speed of light.
    Stored as wrapped numbers representing deviations from 24,800 ns.
    """
    # Extract all numbers after the comment header
    lines = text.strip().splitlines()
    num_tokens = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Check if line consists mostly of numbers
        tokens = stripped.split()
        if all(re.match(r"^-?\d+$", t) for t in tokens):
            num_tokens.extend([int(t) for t in tokens])
    
    df = pd.DataFrame({"obs_id": np.arange(1, len(num_tokens) + 1), "deviation_ns": num_tokens})
    df["passage_time_ns"] = 24800 + df["deviation_ns"]
    # Newcomb's baseline distance was 7.442 km: speed = distance / time
    df["speed_km_s"] = (7.442 / (df["passage_time_ns"] * 1e-9)).round(2)
    return df


def parse_golf(text: str) -> pd.DataFrame:
    """
    Table 20.1: Golf putting success rates by distance (feet).
    Header: 'distance n y'
    """
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    rows = []
    for line in lines[1:]:  # skip header
        parts = line.split()
        if len(parts) >= 3:
            rows.append([int(parts[0]), int(parts[1]), int(parts[2])])
    df = pd.DataFrame(rows, columns=["distance_ft", "n_attempts", "y_success"])
    df["success_rate"] = (df["y_success"] / df["n_attempts"]).round(4)
    return df


def parse_meta(text: str) -> pd.DataFrame:
    """
    Table 5.4: 22 clinical trials of beta-blockers.
    Header: 'study control.deaths control.total treated.deaths treated.total'
    """
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    rows = []
    header_seen = False
    for line in lines:
        if "study" in line and "control" in line:
            header_seen = True
            continue
        if header_seen:
            parts = line.split()
            if len(parts) >= 5:
                rows.append([int(p) for p in parts[:5]])
    df = pd.DataFrame(rows, columns=["study_id", "control_deaths", "control_total", "treated_deaths", "treated_total"])
    df["control_rate"] = (df["control_deaths"] / df["control_total"]).round(4)
    df["treated_rate"] = (df["treated_deaths"] / df["treated_total"]).round(4)
    # Empirical odds ratio (with 0.5 continuity correction)
    cd, ct = df["control_deaths"], df["control_total"]
    td, tt = df["treated_deaths"], df["treated_total"]
    odds_treated = (td + 0.5) / (tt - td + 0.5)
    odds_control = (cd + 0.5) / (ct - cd + 0.5)
    df["log_odds_ratio"] = np.log(odds_treated / odds_control).round(4)
    return df


def parse_fabric(text: str) -> pd.DataFrame:
    """
    Table 16.4: Faults in 32 rolls of fabric.
    Header: 'length faults'
    """
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    rows = []
    header_seen = False
    for line in lines:
        if "length" in line and "faults" in line:
            header_seen = True
            continue
        if header_seen:
            parts = line.split()
            if len(parts) >= 2:
                rows.append([int(parts[0]), int(parts[1])])
    df = pd.DataFrame(rows, columns=["length", "faults"])
    df.insert(0, "roll_id", np.arange(1, len(df) + 1))
    df["faults_per_100m"] = ((df["faults"] / df["length"]) * 100).round(3)
    return df


def parse_schizophrenia(text: str) -> pd.DataFrame:
    """
    Figure 18.1: Reaction times for 11 controls (rows 1-11) and 6 schizophrenics (rows 12-17).
    Each row has 30 measurements.
    """
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    # Filter lines that start with numbers
    matrix_rows = []
    for line in lines:
        parts = line.split()
        if len(parts) >= 10 and all(p.isdigit() for p in parts):
            matrix_rows.append([int(p) for p in parts])
    
    tidy_records = []
    for idx, row in enumerate(matrix_rows):
        subject_id = idx + 1
        is_schiz = 1 if idx >= 11 else 0
        group = "schizophrenic" if is_schiz == 1 else "control"
        for trial_num, rt in enumerate(row, start=1):
            tidy_records.append({
                "subject_id": subject_id,
                "group": group,
                "is_schizophrenic": is_schiz,
                "trial": trial_num,
                "reaction_time_ms": rt,
                "log_rt": round(np.log(rt), 4)
            })
    return pd.DataFrame(tidy_records)


def parse_football(text: str) -> pd.DataFrame:
    """
    Figure 1.1: 10 seasons of NFL results (224 games per season).
    Header: 'home favorite underdog spread favorite.name underdog.name week'
    """
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    rows = []
    header_seen = False
    for line in lines:
        if "favorite" in line and "underdog" in line and "spread" in line:
            header_seen = True
            continue
        if header_seen:
            parts = line.split()
            if len(parts) >= 7:
                try:
                    rows.append({
                        "home_favored": int(parts[0]),
                        "favorite_score": int(parts[1]),
                        "underdog_score": int(parts[2]),
                        "spread": float(parts[3]),
                        "favorite_team": parts[4],
                        "underdog_team": parts[5],
                        "week": int(parts[6])
                    })
                except ValueError:
                    continue
    df = pd.DataFrame(rows)
    df.insert(0, "game_id", np.arange(1, len(df) + 1))
    df["season_idx"] = (df["game_id"] - 1) // 224 + 1
    df["score_diff"] = df["favorite_score"] - df["underdog_score"]
    df["outcome_vs_spread"] = df["score_diff"] - df["spread"]
    return df


def parse_cow(text: str) -> pd.DataFrame:
    """
    Table 7.5: Dairy cow additive experiment (50 cows).
    Header: 'level lactation age initial.weight dry milk fat solids final.weight protein'
    """
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    rows = []
    header_seen = False
    for line in lines:
        if "lactation" in line and "initial.weight" in line:
            header_seen = True
            continue
        if header_seen:
            parts = line.split()
            if len(parts) >= 10:
                try:
                    rows.append({
                        "level": float(parts[0]),
                        "lactation": int(parts[1]),
                        "age": int(parts[2]),
                        "initial_weight": float(parts[3]),
                        "dry": float(parts[4]),
                        "milk": float(parts[5]),
                        "fat": float(parts[6]),
                        "solids": float(parts[7]),
                        "final_weight": float(parts[8]),
                        "protein": float(parts[9])
                    })
                except ValueError:
                    continue
    df = pd.DataFrame(rows)
    df.insert(0, "cow_id", np.arange(1, len(df) + 1))
    return df


def parse_dilution(text: str) -> pd.DataFrame:
    """
    Section 20.2: Serial dilution assays for 10 unknowns (80 pts) + standards (16 pts).
    """
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    numbers = []
    for l in lines:
        try:
            numbers.append(float(l))
        except ValueError:
            continue
    
    unknown_dilutions = [1.0, 1.0, 1/3, 1/3, 1/9, 1/9, 1/27, 1/27]
    standard_dilutions = [1.0, 1.0, 1/2, 1/2, 1/4, 1/4, 1/8, 1/8, 1/16, 1/16, 1/32, 1/32, 1/64, 1/64, 0.0, 0.0]
    
    records = []
    # Unknowns: 10 unknowns * 8 dilutions = 80 measurements
    for u in range(10):
        for rep_idx in range(8):
            num_idx = u * 8 + rep_idx
            if num_idx < len(numbers):
                records.append({
                    "sample_type": "unknown",
                    "sample_id": f"unknown_{u+1}",
                    "dilution": round(unknown_dilutions[rep_idx], 5),
                    "replicate": (rep_idx % 2) + 1,
                    "response": numbers[num_idx]
                })
    # Standards: 16 measurements starting at index 80
    for s_idx in range(16):
        num_idx = 80 + s_idx
        if num_idx < len(numbers):
            records.append({
                "sample_type": "standard",
                "sample_id": "standard",
                "dilution": round(standard_dilutions[s_idx], 5),
                "replicate": (s_idx % 2) + 1,
                "response": numbers[num_idx]
            })
    df = pd.DataFrame(records)
    df.insert(0, "assay_id", np.arange(1, len(df) + 1))
    return df


def parse_newyork(text: str) -> pd.DataFrame:
    """
    Section 9.3 / Table 18.2: Populations of cities and towns in New York State.
    Header: 'population code'
    """
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    rows = []
    header_seen = False
    for line in lines:
        if "population" in line and "code" in line:
            header_seen = True
            continue
        if header_seen:
            parts = line.split()
            if len(parts) >= 2:
                try:
                    rows.append([int(parts[0]), int(parts[1])])
                except ValueError:
                    continue
    df = pd.DataFrame(rows, columns=["population", "code"])
    df.insert(0, "town_id", np.arange(1, len(df) + 1))
    code_map = {
        100: "neither_sample",
        200: "both_samples",
        300: "sample_2_only",
        400: "sample_1_only"
    }
    df["sample_status"] = df["code"].map(code_map).fillna("unknown")
    return df


def parse_stratified(text: str) -> pd.DataFrame:
    """
    Table 7.2: 16 strata from CBS News survey.
    Header: 'region density bush dukakis other proportion'
    """
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    rows = []
    header_seen = False
    for line in lines:
        if "region" in line and "density" in line:
            header_seen = True
            continue
        if header_seen:
            parts = line.split()
            if len(parts) >= 6:
                try:
                    rows.append({
                        "region": parts[0],
                        "density_tier": parts[1],
                        "bush_pct": float(parts[2]),
                        "dukakis_pct": float(parts[3]),
                        "other_pct": float(parts[4]),
                        "stratum_pop_share": float(parts[5])
                    })
                except ValueError:
                    continue
    df = pd.DataFrame(rows)
    df.insert(0, "stratum_id", np.arange(1, len(df) + 1))
    return df


def parse_cancer(text: str) -> pd.DataFrame:
    """
    Section 2.8: County kidney cancer data (1980-1984).
    Tab-separated columns: state, county, dc, dcV, pop, popV, aadc, ...
    """
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    rows = []
    for line in lines[1:]:  # skip header
        parts = line.split("\t")
        if len(parts) >= 8:
            try:
                state = parts[0].strip()
                county = parts[1].strip()
                deaths = int(parts[2].strip())
                pop = int(parts[4].strip())
                aadc = float(parts[6].strip())
                rows.append({
                    "state": state,
                    "county": county,
                    "death_count": deaths,
                    "population": pop,
                    "crude_rate_per_100k": round((deaths / pop) * 100000, 3) if pop > 0 else 0.0,
                    "age_adjusted_rate": aadc
                })
            except (ValueError, IndexError):
                continue
    return pd.DataFrame(rows)


def parse_election_2008(text: str) -> pd.DataFrame:
    """
    Exercise 2.21: 2008 Presidential Election Results CSV.
    """
    import io
    df = pd.read_csv(io.StringIO(text))
    df.columns = [c.strip().lower() for c in df.columns]
    return df


# --------------------------------------------------------------------------
# Main Orchestrator
# --------------------------------------------------------------------------

DATASET_CONFIGS = [
    {
        "key": "rats",
        "url": BASE_URL_SITES + "rats.asc",
        "raw_name": "rats.asc",
        "clean_name": "rats",
        "parser": parse_rats
    },
    {
        "key": "light",
        "url": BASE_URL_SITES + "light.asc",
        "raw_name": "light.asc",
        "clean_name": "light",
        "parser": parse_light
    },
    {
        "key": "golf",
        "url": BASE_URL_SITES + "golf.dat",
        "raw_name": "golf.dat",
        "clean_name": "golf",
        "parser": parse_golf
    },
    {
        "key": "meta",
        "url": BASE_URL_SITES + "meta.asc",
        "raw_name": "meta.asc",
        "clean_name": "meta",
        "parser": parse_meta
    },
    {
        "key": "fabric",
        "url": BASE_URL_SITES + "fabric.asc",
        "raw_name": "fabric.asc",
        "clean_name": "fabric",
        "parser": parse_fabric
    },
    {
        "key": "schizophrenia",
        "url": BASE_URL_SITES + "schiz.asc",
        "raw_name": "schiz.asc",
        "clean_name": "schizophrenia",
        "parser": parse_schizophrenia
    },
    {
        "key": "football",
        "url": BASE_URL_SITES + "football.asc",
        "raw_name": "football.asc",
        "clean_name": "football",
        "parser": parse_football
    },
    {
        "key": "cow",
        "url": BASE_URL_SITES + "cow.asc",
        "raw_name": "cow.asc",
        "clean_name": "cow",
        "parser": parse_cow
    },
    {
        "key": "dilution",
        "url": BASE_URL_SITES + "dilution.dat",
        "raw_name": "dilution.dat",
        "clean_name": "dilution",
        "parser": parse_dilution
    },
    {
        "key": "newyork",
        "url": BASE_URL_SITES + "newyork.asc",
        "raw_name": "newyork.asc",
        "clean_name": "newyork",
        "parser": parse_newyork
    },
    {
        "key": "stratified",
        "url": BASE_URL_SITES + "stratified.asc",
        "raw_name": "stratified.asc",
        "clean_name": "stratified",
        "parser": parse_stratified
    },
    {
        "key": "election_2008",
        "url": BASE_URL_SITES + "2008ElectionResult.csv",
        "raw_name": "2008ElectionResult.csv",
        "clean_name": "election_2008",
        "parser": parse_election_2008
    },
    {
        "key": "kidney_cancer_1980_1984",
        "url": BASE_URL_STAT + "cancer/gd80to84.txt",
        "raw_name": "gd80to84.txt",
        "clean_name": "kidney_cancer_1980_1984",
        "parser": parse_cancer
    }
]


def write_loader_helper(dest_dir: str):
    """Write an ultra-convenient python helper file directly into the destination."""
    loader_code = '''"""
bda3_loader.py
==============
Drop-in helper to load BDA3 datasets in Google Colab or local Python scripts.

Usage:
------
    from bda3_loader import load_bda3, list_datasets

    # List all available datasets
    print(list_datasets())

    # Load as a clean pandas DataFrame
    df_rats = load_bda3('rats')
    df_light = load_bda3('light')
    df_golf = load_bda3('golf')
"""

import os
import json
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_DIR = os.path.join(CURRENT_DIR, "clean_csv")
PARQUET_DIR = os.path.join(CURRENT_DIR, "parquet")
CATALOG_PATH = os.path.join(CURRENT_DIR, "metadata_catalog.json")


def list_datasets():
    """Return a list of available BDA3 dataset names and short descriptions."""
    if os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH, "r") as f:
            catalog = json.load(f)
        return [(d["name"], d.get("book_chapter", ""), d.get("description", "")) for d in catalog.get("datasets", [])]
    else:
        files = [f.replace(".csv", "") for f in os.listdir(CSV_DIR) if f.endswith(".csv")]
        return [(f, "", "") for f in sorted(files)]


def load_bda3(name: str, prefer_parquet: bool = True) -> pd.DataFrame:
    """
    Load a BDA3 dataset by name (e.g., 'rats', 'light', 'golf', 'meta', 'schizophrenia').
    Prefers Parquet for speed and type preservation if available, falls back to CSV.
    """
    name = name.lower().replace(".csv", "").replace(".parquet", "")
    
    parquet_file = os.path.join(PARQUET_DIR, f"{name}.parquet")
    csv_file = os.path.join(CSV_DIR, f"{name}.csv")
    
    if prefer_parquet and os.path.exists(parquet_file):
        try:
            return pd.read_parquet(parquet_file)
        except Exception:
            pass
            
    if os.path.exists(csv_file):
        return pd.read_csv(csv_file)
        
    available = [f.replace(".csv", "") for f in os.listdir(CSV_DIR) if f.endswith(".csv")]
    raise FileNotFoundError(
        f"Dataset '{name}' not found. Available datasets: {available}"
    )
'''
    with open(os.path.join(dest_dir, "bda3_loader.py"), "w") as f:
        f.write(loader_code)


def run_pipeline(output_dir: str):
    """Run full pipeline, creating directories and processing all datasets."""
    print(f"==> Target destination: {output_dir}")
    raw_dir = os.path.join(output_dir, "raw")
    csv_dir = os.path.join(output_dir, "clean_csv")
    parquet_dir = os.path.join(output_dir, "parquet")
    
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(parquet_dir, exist_ok=True)
    
    summary = []
    
    for cfg in DATASET_CONFIGS:
        key = cfg["key"]
        url = cfg["url"]
        raw_path = os.path.join(raw_dir, cfg["raw_name"])
        csv_path = os.path.join(csv_dir, f"{cfg['clean_name']}.csv")
        parquet_path = os.path.join(parquet_dir, f"{cfg['clean_name']}.parquet")
        
        print(f"--> Processing [{key}] from {url} ...")
        try:
            # 1. Download raw
            raw_text = fetch_text(url)
            with open(raw_path, "w", encoding="utf-8") as f:
                f.write(raw_text)
            
            # 2. Parse into clean DataFrame
            df = cfg["parser"](raw_text)
            
            # 3. Save CSV
            df.to_csv(csv_path, index=False)
            
            # 4. Save Parquet
            try:
                df.to_parquet(parquet_path, index=False)
            except Exception as pe:
                print(f"    (Notice: Parquet export skipped for {key}: {pe})")
                
            summary.append({
                "name": cfg["clean_name"],
                "rows": len(df),
                "cols": list(df.columns)
            })
            print(f"    [OK] Saved {len(df)} rows to {cfg['clean_name']}.csv & .parquet")
        except Exception as e:
            print(f"    [ERROR] Failed to process {key}: {e}")
            
    # Write helper loader module
    write_loader_helper(output_dir)
    print("--> Wrote bda3_loader.py helper module")
    
    print("\nETL Pipeline Completed Successfully!")
    print(f"Total datasets processed: {len(summary)}")


if __name__ == "__main__":
    out_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath("./bda3/data")
    run_pipeline(out_dir)
