"""
CGWB Groundwater Data Preprocessing Script
==========================================

This script addresses all identified data quality and metadata issues:
1. Removes embedded header rows
2. Fixes latitude–longitude swaps
3. Converts non-numeric values to proper numeric format
4. Handles missing values
5. Validates geographic coordinates
6. Standardizes column names
7. Canonicalizes district names (aggregation-safe)
8. Preserves raw text metadata
9. Produces final analysis-ready dataset

Author: Research Team
Date: February 2026
"""

from pathlib import Path
import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")


# -------------------------------------------------------------------
# DATA LOADING
# -------------------------------------------------------------------
def load_data(filepath: Path) -> pd.DataFrame:
    print("Loading data...")
    df = pd.read_csv(filepath, encoding="utf-8", low_memory=False)
    print(f"Initial shape: {df.shape}")
    return df


# -------------------------------------------------------------------
# CORE CLEANING STEPS (UNCHANGED LOGIC)
# -------------------------------------------------------------------
def remove_header_rows(df):
    print("\n1. Removing embedded header rows...")
    header_mask = df["State"] == "State"
    if header_mask.any():
        df = df.loc[~header_mask].copy()
        print(f"   Removed {header_mask.sum()} header rows")
    return df


def fix_coordinate_swaps(df):
    print("\n2. Fixing latitude–longitude swaps...")
    swap_mask = (df["Latitude"] > 60) & (df["Longitude"] < 40)
    if swap_mask.any():
        df.loc[swap_mask, ["Latitude", "Longitude"]] = df.loc[
            swap_mask, ["Longitude", "Latitude"]
        ].values
        print(f"   Corrected {swap_mask.sum()} swapped coordinates")
    return df


def validate_coordinates(df):
    print("\n3. Validating coordinates...")
    invalid_mask = (
        (df["Latitude"] < 6) | (df["Latitude"] > 38) |
        (df["Longitude"] < 66) | (df["Longitude"] > 99)
    )
    if invalid_mask.any():
        df.loc[invalid_mask, "coordinate_flag"] = "INVALID"
        print(f"   Flagged {invalid_mask.sum()} invalid coordinates")
    return df


def clean_numeric_columns(df):
    print("\n4. Cleaning numeric columns...")
    numeric_cols = ["EC (µS/cm at", "HCO3", "SO4", "NO3", "PO4", "Total Hardness"]
    replacements = {"-": np.nan, "BDL": 0, "#REF!": np.nan, "0..00": 0}

    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].replace(replacements)
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def handle_duplicate_locations(df):
    print("\n5. Handling duplicate locations...")
    key_cols = ["State", "District", "Location"]
    if df.duplicated(subset=key_cols).any():
        df["null_count"] = df.isna().sum(axis=1)
        df = (
            df.sort_values("null_count")
              .drop_duplicates(subset=key_cols, keep="first")
              .drop(columns="null_count")
        )
    return df


def validate_parameter_ranges(df):
    print("\n6. Validating parameter ranges...")
    param_ranges = {
        "pH": (0, 14),
        "EC (µS/cm at": (0, 100000),
        "NO3": (0, 1000),
    }
    for p, (lo, hi) in param_ranges.items():
        if p in df.columns:
            mask = (df[p] < lo) | (df[p] > hi)
            if mask.any():
                df.loc[mask, f"{p}_extreme_flag"] = True
    return df


# -------------------------------------------------------------------
# METADATA STANDARDIZATION (NEW, SAFE)
# -------------------------------------------------------------------
def standardize_metadata(df):
    print("\n7. Standardizing metadata...")

    # Preserve raw text
    df["district_raw"] = df["District"]
    df["location_raw"] = df["Location"]

    # District canonicalization (aggregation-safe)
    district_aliases = {
        "allahabad": "prayagraj",
        "allahabad prayagraj": "prayagraj",
        "bangalore urban": "bengaluru urban",
        "shimoga": "shivamogga",
        "e singhbum": "east singhbhum",
        "w singhbum": "west singhbhum",
        "devbhoomi dwarka": "devbhumi dwarka",
    }

    df["district_clean"] = (
        df["District"]
        .str.lower()
        .str.replace(r"[^a-z\s]", "", regex=True)
        .replace(district_aliases)
    )

    # Spatially stable location ID (preferred over names)
    df["location_id"] = (
        df["Latitude"].round(4).astype(str) + "_" +
        df["Longitude"].round(4).astype(str)
    )

    # Record ID for reproducibility
    df = df.reset_index(drop=True)
    df["record_id"] = df.index

    return df


# -------------------------------------------------------------------
# COLUMN NAME STANDARDIZATION
# -------------------------------------------------------------------
def standardize_column_names(df):
    print("\n8. Standardizing column names...")

    rename_map = {
        "EC (µS/cm at": "EC_uScm",
        "CO3 (mg/L)": "CO3_mgL",
        "HCO3": "HCO3_mgL",
        "Cl (mg/L)": "Cl_mgL",
        "F (mg/L)": "F_mgL",
        "Ca (mg/L)": "Ca_mgL",
        "Mg (mg/L)": "Mg_mgL",
        "Na (mg/L)": "Na_mgL",
        "K (mg/L)": "K_mgL",
        "Fe (ppm)": "Fe_ppm",
        "As (ppb)": "As_ppb",
        "U (ppb)": "U_ppb",
        "Total Hardness": "Total_Hardness_mgL",
    }

    return df.rename(columns=rename_map)


# -------------------------------------------------------------------
# SAVE OUTPUT
# -------------------------------------------------------------------
def save_final_data(df, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\n✓ Final cleaned dataset saved: {output_path}")


# -------------------------------------------------------------------
# MAIN PIPELINE
# -------------------------------------------------------------------
def main():
    print("=" * 80)
    print("CGWB FINAL PREPROCESSING PIPELINE")
    print("=" * 80)

    PROJECT_ROOT = Path(__file__).resolve().parents[1]

    input_file = PROJECT_ROOT / "data" / "raw" / "groundwater_data_edited.csv"
    output_file = PROJECT_ROOT / "data" / "cleaned" / "groundwater_data_cleaned_final.csv"

    df = load_data(input_file)

    df = (
        df.pipe(remove_header_rows)
          .pipe(fix_coordinate_swaps)
          .pipe(validate_coordinates)
          .pipe(clean_numeric_columns)
          .pipe(handle_duplicate_locations)
          .pipe(validate_parameter_ranges)
          .pipe(standardize_metadata)
          .pipe(standardize_column_names)
    )

    save_final_data(df, output_file)

    print("\nFINAL PREPROCESSING COMPLETE ✔")
    print(f"Final rows: {len(df)}, columns: {len(df.columns)}")
    return df


if __name__ == "__main__":
    main()
