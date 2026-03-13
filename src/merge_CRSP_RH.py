"""
merge_CRSP_RH.py

Script for merging the CRSP and Robintrack data for the bachelor thesis.
This file contains the functions and procedures to merge and preprocess the CRSP and Robintrack data.

© 2026 Yvan Richard, University of St. Gallen
"""

# Importing necessary libraries
import pandas as pd
import numpy as np
import os
import warnings

# Importing configuration
from config import CRSP_DATA_INTERIM_PATH, CRSP_DATA_PROCESSED_PATH, ROBINTRACK_DATA_PROCESSED_PATH

def merge_crsp_rh():
    """
    Format of the two data frames:
    1) CRSP
    -------
    permno,date,ret,prc,vol,shrout,ticker,exchcd
    10026,2018-05-01,-0.038862,132.07001,102619.0,18702.0,JJSF,3.0

    2) Robintrack
    --------------
    date,users_close,users_last,ticker
    2018-06-01,70.0,70.0,RIV

    The goal is to merge the two data frames on the date and ticker columns,
    keeping only the rows that have a match in the CRSP data frame. This is
    important because I only want tickers that are in the CRSP data frame.

    The format of the merged data frame will be as follows:
    permno,date,ret,prc,vol,shrout,ticker,exchcd,users_close,users_last
    """

    # 1) Read the cleaned CRSP data and the cleaned Robintrack data
    crsp_df = pd.read_csv(os.path.join(CRSP_DATA_INTERIM_PATH, "CRSP_cleaned_a.csv"))
    rh_df = pd.read_csv(os.path.join(ROBINTRACK_DATA_PROCESSED_PATH, "robintrack_merged.csv"))

    # 2) Merge the two data frames on the date and ticker columns, keeping only the rows that have a match in the CRSP data frame
    merged_df = pd.merge(crsp_df, rh_df, on=["date", "ticker"], how="inner")

    # 3) Save the merged data frame to the processed directory
    merged_df.to_csv(os.path.join(CRSP_DATA_PROCESSED_PATH, "CRSP_RH_merged.csv"), index=False)


if __name__ == "__main__":
    print("\nMerging CRSP and Robintrack data...\n")
    merge_crsp_rh()
    print("\nCRSP and Robintrack data merged successfully!\n")

