"""
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
