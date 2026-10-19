"""
bda3_loader.py
==============
Universal data loader for BDA3 (Bayesian Data Analysis, 3rd ed.) datasets.
Provides seamless access whether running locally or inside Google Colab mounted to Google Drive.

Usage:
------
    from bda3_loader import load_bda3, list_datasets

    # View all available datasets:
    for name, ch, desc in list_datasets():
        print(f"{name:15} | {ch:25} | {desc[:40]}...")

    # Load as a pandas DataFrame:
    df_rats = load_bda3('rats')
    df_light = load_bda3('light')
    df_golf = load_bda3('golf')
"""

import os
import json
import pandas as pd
from typing import List, Tuple

# Possible root directories to search (local repo or Google Drive paths)
POSSIBLE_DIRS = [
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data"),
    "/content/drive/MyDrive/BDA3_Data",
    "/content/drive/MyDrive/BDA3/data",
    "/content/BDA3_Data",
    os.path.abspath("./bda3/data"),
    os.path.abspath("./data")
]


def _find_data_dir() -> str:
    """Find the first existing data directory containing clean_csv/."""
    for d in POSSIBLE_DIRS:
        if os.path.exists(os.path.join(d, "clean_csv")):
            return os.path.abspath(d)
    # Default to the local data dir even if not created yet
    return os.path.abspath(POSSIBLE_DIRS[0])


def list_datasets() -> List[Tuple[str, str, str]]:
    """Return a list of available BDA3 dataset names, book chapters, and descriptions."""
    data_dir = _find_data_dir()
    catalog_path = os.path.join(data_dir, "dataset_catalog.json")
    
    if os.path.exists(catalog_path):
        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog = json.load(f)
        return [
            (
                d["name"],
                d.get("book_chapter", ""),
                d.get("description", "")
            )
            for d in catalog.get("datasets", [])
        ]
    
    csv_dir = os.path.join(data_dir, "clean_csv")
    if os.path.exists(csv_dir):
        files = [f.replace(".csv", "") for f in os.listdir(csv_dir) if f.endswith(".csv")]
        return [(f, "", "") for f in sorted(files)]
    
    return []


def load_bda3(name: str, prefer_parquet: bool = True) -> pd.DataFrame:
    """
    Load a BDA3 dataset by name (e.g., 'rats', 'light', 'golf', 'meta', 'schizophrenia').
    
    Parameters:
    -----------
    name : str
        Dataset identifier (case-insensitive, e.g. 'rats', 'light', 'golf').
    prefer_parquet : bool
        If True, attempts to load the faster Parquet format first, falling back to CSV.
        
    Returns:
    --------
    pd.DataFrame
        Cleaned, typed, tidy DataFrame ready for analysis and PyMC modeling.
    """
    data_dir = _find_data_dir()
    clean_name = name.lower().strip().replace(".csv", "").replace(".parquet", "")
    
    parquet_path = os.path.join(data_dir, "parquet", f"{clean_name}.parquet")
    csv_path = os.path.join(data_dir, "clean_csv", f"{clean_name}.csv")
    
    if prefer_parquet and os.path.exists(parquet_path):
        try:
            return pd.read_parquet(parquet_path)
        except Exception:
            pass
            
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
        
    available = [item[0] for item in list_datasets()]
    raise FileNotFoundError(
        f"Dataset '{clean_name}' not found in {data_dir}.\n"
        f"Available datasets: {available}\n"
        f"Run prepare_bda3_data.py to download and generate them."
    )
