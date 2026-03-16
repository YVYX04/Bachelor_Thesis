"""
CRSP and RH TAQ merging script.
This script merges the cleaned TAQ data with the merged CRSP and Robintrack data on the
date and ticker columns. The resulting merged data frame is saved to the processed directory.

© 2026 Yvan Richard, University of St. Gallen
"""

# Importing necessary libraries
import pandas as pd
import os
import warnings
import numpy as np

# Importing configuration
from src.config import PROCESSED_DATA_PATH, RAW_DATA_PATH, INTERIM_DATA_PATH

def merge_crsp_rh_taq():
    # 1) Read the merged CRSP and Robintrack data and the cleaned TAQ data
    try:
        crsp_rh_df = pd.read_csv(os.path.join(PROCESSED_DATA_PATH, "CRSP_RH_merged.csv"))
        taq_df = pd.read_csv(os.path.join(INTERIM_DATA_PATH, "TAQ_cleaned.csv"))
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # 2) Convert the date columns to datetime format and ensure ticker columns are uppercase and stripped
    crsp_rh_df["date"] = pd.to_datetime(crsp_rh_df["date"]).dt.normalize()
    crsp_rh_df["ticker"] = crsp_rh_df["ticker"].astype(str).str.upper().str.strip()
    taq_df["date"] = pd.to_datetime(taq_df["date"]).dt.normalize()
    taq_df["ticker"] = taq_df["ticker"].astype(str).str.upper().str.strip()

    # 3) Merge the two data frames on the date and ticker columns
    merged_df = pd.merge(crsp_rh_df, taq_df, on=["date", "ticker"], how="left")

    # 4) Report on missing values for each column after the merge
    missing_report = merged_df.isnull().sum()
    print("\nMERGE CRSP/RH with TAQ REPORT\n")
    print("\nLength of merged data frame:", len(merged_df))
    print("\nMissing values after merging CRSP/RH with TAQ data:")
    print(missing_report)
    print("\n")

    # 5) Save the merged data frame to the processed directory
    merged_df.to_csv(os.path.join(PROCESSED_DATA_PATH, "CRSP_RH_TAQ_merged.csv"), index=False)


if __name__ == "__main__":
    print("\nMerging CRSP/RH data with TAQ data...\n")
    merge_crsp_rh_taq()
    print("\nCRSP/RH and TAQ data merged successfully!\n")

