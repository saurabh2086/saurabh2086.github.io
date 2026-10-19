# Bayesian Data Analysis (BDA3) Datasets for Python & PyMC

This directory and the accompanying tools provide a curated, clean, and standardized library of the official datasets from Andrew Gelman et al.'s textbook **_Bayesian Data Analysis_ (3rd Edition)**, originally hosted at [Columbia University Statistics](https://sites.stat.columbia.edu/gelman/book/data/).

---

## 🎯 The Motivation: Why Cleaning is Required

The original datasets on Gelman's server were created decades ago in `.asc` and `.dat` formats:
- **Embedded Comments**: Explanatory text, notes, and citations are mixed directly into the first few lines of files (e.g., `rats.asc`, `fabric.asc`), causing standard `pd.read_csv()` to fail with parser errors.
- **Unstructured / Matrix Layouts**: Files like `light.asc` (Simon Newcomb's speed of light) are line-wrapped lists of 66 numbers without variable headers; `schiz.asc` stores reaction times as fixed matrices of 11 control and 6 schizophrenic subjects separated by blank lines; `dilution.dat` embeds an entire serial dilution titration assay protocol into 96 unlabelled numbers.
- **Variable Whitespace Delimiters**: Custom spaces and irregular indentation break simple table parsers.

### The Solution
We provide an automated ETL pipeline that downloads every dataset, strips header comments, converts them into **tidy, typed Pandas DataFrames** in both **CSV** (universal inspection) and **Parquet** (high-speed zero-overhead columnar storage), and saves them directly to your **Google Drive** for seamless use in **Google Colab**.

---

## 📁 Directory & Google Drive Structure

When you run the setup in Google Colab, your Google Drive will be organized as follows:

```
Google Drive/
└── MyDrive/
    ├── BDA3_Data/
    │   ├── clean_csv/                  # Universal, human-readable tidy CSVs
    │   │   ├── rats.csv
    │   │   ├── light.csv
    │   │   ├── golf.csv
    │   │   ├── meta.csv
    │   │   ├── fabric.csv
    │   │   ├── schizophrenia.csv
    │   │   ├── football.csv
    │   │   ├── cow.csv
    │   │   ├── dilution.csv
    │   │   ├── newyork.csv
    │   │   ├── stratified.csv
    │   │   ├── election_2008.csv
    │   │   └── kidney_cancer_1980_1984.csv
    │   ├── parquet/                    # High-performance, schema-typed files
    │   │   ├── rats.parquet
    │   │   ├── light.parquet
    │   │   └── ...
    │   ├── raw/                        # Original unaltered files from Columbia
    │   │   ├── rats.asc
    │   │   ├── light.asc
    │   │   └── ...
    │   ├── bda3_loader.py              # Drop-in Python helper module
    │   └── dataset_catalog.json        # Machine-readable schema & metadata
    └── BDA3_Figures/                   # High-resolution (300 DPI) publication figures
        ├── ch03_speed_of_light_robust_model.png
        ├── ch05_rat_tumors_shrinkage_partial_pooling.png
        └── ch20_golf_putting_geometry_model.png
```

---

## 🚀 Quickstart in Google Colab

### Step 1: Open the Colab Notebook
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/saurabh2086/saurabh2086.github.io/blob/main/bda3/notebooks/bda3_google_drive_setup_and_pymc.ipynb)

Open [`bda3_google_drive_setup_and_pymc.ipynb`](https://colab.research.google.com/github/saurabh2086/saurabh2086.github.io/blob/main/bda3/notebooks/bda3_google_drive_setup_and_pymc.ipynb) directly in Google Colab.

### Step 2: Mount Google Drive
Run the first cell:
```python
from google.colab import drive
drive.mount('/content/drive')
```

### Step 3: Run the Automated ETL
Run the ETL cell in the notebook. In under 15 seconds, all datasets are downloaded, converted, and saved to `/content/drive/MyDrive/BDA3_Data`.

### Step 4: Load Any Dataset in One Line
In any current or future Colab notebook, load datasets directly:
```python
import sys
sys.path.append('/content/drive/MyDrive/BDA3_Data')
from bda3_loader import load_bda3

# Load clean DataFrames ready for PyMC
df_rats = load_bda3('rats')
df_light = load_bda3('light')
df_golf = load_bda3('golf')
```

---

## 📊 Dataset Catalog & PyMC Use Cases

| Dataset Key | BDA3 Chapter | Book Reference | Description | Recommended PyMC Model |
| :--- | :--- | :--- | :--- | :--- |
| **`rats`** | Chapter 5 | Table 5.1 | Tumor incidence in 71 historical control groups of rats | Hierarchical Beta-Binomial / Logit-Normal with partial pooling / shrinkage |
| **`light`** | Chapter 3 | Figure 3.1 / Table 3.1 | Simon Newcomb's 66 speed of light measurements | Comparison of Gaussian vs. Robust Student-$t$ likelihood (handling $-44$ outlier) |
| **`golf`** | Chapter 20 | Table 20.1 | Professional golf putting success by distance (2 to 20 ft) | Non-linear physical geometry model ($\arcsin$) vs. logistic regression |
| **`meta`** | Chapter 5 | Table 5.4 | 22 clinical trials of beta-blockers post myocardial infarction | Hierarchical random-effects meta-analysis for odds ratios |
| **`fabric`** | Chapter 16 | Table 16.4 | Faults in 32 rolls of fabric of varying lengths | Poisson regression with $\log(\text{length})$ offset or Negative-Binomial |
| **`schizophrenia`**| Chapter 18 | Figure 18.1 | Reaction times for 11 controls and 6 schizophrenics | Finite mixture model with subject random effects & attentional lapse component |
| **`football`** | Chapter 1 | Figure 1.1 | NFL game scores and point spreads over 10 seasons | Point spread efficiency test & Gaussian score differential modeling |
| **`cow`** | Chapter 7 | Table 7.5 | Milk yield and fat/solids of 50 cows with dietary additives | Covariate adjustment / causal inference with baseline balance |
| **`dilution`** | Chapter 20 | Section 20.2 | Serial dilution assays for 10 unknowns + standards | 4-parameter logistic / sigmoidal non-linear calibration curve |
| **`newyork`** | Chapter 9 / 18| Section 9.3 | 1960 New York State town populations and sampling codes | Finite population inference & capture-recapture sampling |
| **`stratified`** | Chapter 7 | Table 7.2 | 1988 CBS pre-election survey across 16 strata | Multilevel Regression with Post-stratification (MRP) |
| **`election_2008`**| Chapter 2 | Exercise 2.21 | State-level Obama vs. McCain vote shares & electoral votes | Bayesian state poll aggregation & electoral college forecasting |
| **`kidney_cancer_1980_1984`**| Chapter 2 | Section 2.8 | US county kidney cancer death rates and population | Empirical Bayes & spatial Poisson smoothing (the small-sample map artifact) |

---

## 🎨 Exporting Figures for Web Articles

The Colab notebook is pre-configured with publication-ready styling (clean minimalist typography, curated color palettes, 300 DPI rasterization, tight bounding boxes).

When you run model checks or visualizations, figures are saved directly to:
```python
fig.savefig('/content/drive/MyDrive/BDA3_Figures/my_figure.png', dpi=300, bbox_inches='tight')
```
You can download them straight from Google Drive or Google Drive desktop sync and insert them directly into your GitHub Pages HTML articles!
