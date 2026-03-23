"""
RP_merging.py

In this script, I merge the 10 RavenPack data sets together.

© 2026 Yvan Richard, University of St. Gallen
"""

# Import necessary libraries
import os
import pandas as pd
import numpy as np

# Import configuration
from src.config import INTERIM_DATA_PATH, PROCESSED_DATA_PATH, RP_COLUMNS

def merge_rp_data(input_files, output_file):
    """
    Merge multiple cleaned RavenPack data files into a single DataFrame.

    Parameters
    ----------
    input_files : list of str
        List of file paths to the cleaned RavenPack CSV files.
    output_file : str
        Path to save the merged output CSV file.
    """
    usecols = ['date', 'ticker', 'num_news', 'num_news_relevant', 'ess', 'css', 'anl_chg']
    merged_df = pd.DataFrame(columns=usecols)

    for file in input_files:
        if os.path.exists(file):
            print(f"Reading {file}...")
            df = pd.read_csv(file, usecols=usecols)
            merged_df = pd.concat([merged_df, df], ignore_index=True)
        else:
            print(f"Warning: file not found -> {file}")

    # Save the merged DataFrame to CSV
    merged_df.to_csv(output_file, index=False)
    print(f"Merged data saved to: {output_file}")

    # Also create a version merged with the main data set
    main = pd.read_csv(os.path.join(PROCESSED_DATA_PATH, "CRSP_RH_TAQ_merged.csv"))
    main["date"] = pd.to_datetime(main["date"])
    merged_df["date"] = pd.to_datetime(merged_df["date"])
    final_merged = pd.merge(main, merged_df, on=["date", "ticker"], how="left")
    final_merged.to_csv(os.path.join(PROCESSED_DATA_PATH, "main.csv"), index=False)
    print(f"Final merged data with main dataset saved to: {os.path.join(PROCESSED_DATA_PATH, 'main.csv')}")
    

if __name__ == "__main__":
    print("\nStart merging RavenPack data...\n")
    input_files = [
        os.path.join(INTERIM_DATA_PATH, f"RP/rp_cleaned_{i:02d}.csv") for i in range(1, 11)
    ]
    output_file = os.path.join(PROCESSED_DATA_PATH, "RP/rp_merged.csv")
    merge_rp_data(input_files, output_file)