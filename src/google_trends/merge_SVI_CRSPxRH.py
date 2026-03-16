"""
merge_SVI_CRSPxRH.py

Script for merging the SVI data with the merged CRSP and Robintrack data for the bachelor thesis.
This file contains the functions and procedures to merge the SVI data with the merged CRSP and
Robintrack data.

© 2026 Yvan Richard, University of St. Gallen
"""

# Importing necessary libraries
import pandas as pd
import os
import warnings
import numpy as np

# Importing configuration
from src.config import PROCESSED_DATA_PATH, TSSVI_INTERIM_PATH

def merge_svi_crsp_rh():
    """
    Function to merge the SVI data with the merged CRSP and Robintrack data.
    This function reads the SVI data and the merged CRSP and Robintrack data, merges them on the date and ticker columns,
    and saves the results to a .csv file in the processed directory.

    The format of the merged data frame will be as follows:
    permno,date,ret,prc,vol,shrout,ticker,exchcd,users_close,users_last,TSSVI
    10026,2018-05-01,-0.038862,132.07001,102619.0,18702.0,JJSF,3.0,70.0,70.0,0.5
    """

    # 1) Read the SVI data and the merged CRSP and Robintrack data
    svi_df = pd.read_csv(os.path.join(TSSVI_INTERIM_PATH, "google_trends_svi.csv"))
    crsp_rh_df = pd.read_csv(os.path.join(PROCESSED_DATA_PATH, "CRSP_RH_merged.csv"))

    # 2) Convert the date columns to datetime format and ensure ticker columns are uppercase and stripped
    svi_df["date"] = pd.to_datetime(svi_df["date"]).dt.normalize()
    svi_df["ticker"] = svi_df["ticker"].astype(str).str.upper().str.strip()
    crsp_rh_df["date"] = pd.to_datetime(crsp_rh_df["date"]).dt.normalize()
    crsp_rh_df["ticker"] = crsp_rh_df["ticker"].astype(str).str.upper().str.strip()

    # Optional: I print the number of tickers in common in both data set
    svi_tickers = set(svi_df["ticker"].dropna().unique())
    crsp_rh_tickers = set(crsp_rh_df["ticker"].dropna().unique())
    common_tickers = svi_tickers.intersection(crsp_rh_tickers)

    print(f"Number of unique tickers in SVI data: {len(svi_tickers)}")
    print(f"Number of unique tickers in CRSP/RH data: {len(crsp_rh_tickers)}")
    print(f"Number of unique tickers in common: {len(common_tickers)}")

    # 3) Merge the two data frames on the date and ticker columns
    # WARNING: I only keep RUSSEL 3000 tickers with this merge.
    merged_df = pd.merge(svi_df, crsp_rh_df, on=["date", "ticker"], how="right")

    # 4) Report on missing values for each column after the merge
    missing_report = merged_df.isnull().sum()
    print("\nLength of merged data frame:", len(merged_df))
    print("\nMissing values after merging SVI with CRSP and Robintrack data:")
    print(missing_report)
    print("\n")

    # 5) Save the merged data frame to the processed directory
    merged_df.to_csv(os.path.join(PROCESSED_DATA_PATH, "CRSP_RH_SVI_merged.csv"), index=False)


if __name__ == "__main__":
    print("\nMerging SVI data with merged CRSP and Robintrack data...\n")
    merge_svi_crsp_rh()
    print("\nSVI data merged with CRSP and Robintrack data successfully!\n")

