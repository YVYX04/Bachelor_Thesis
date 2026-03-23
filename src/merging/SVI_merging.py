"""
SVI_merging.py

In this script, I merge the Google Trends SVI data with the main dataset.
"""

# Import necessary libraries
import os
import pandas as pd

# Import configuration
from src.config import INTERIM_DATA_PATH, PROCESSED_DATA_PATH

def merge_svi_data(svi_file, main_file, output_file):
    """
    Merge the Google Trends SVI data with the main dataset.

    Parameters
    ----------
    svi_file : str
        Path to the Google Trends SVI CSV file.
    main_file : str
        Path to the main dataset CSV file.
    output_file : str
        Path to save the merged output CSV file.
    """
    # Read the SVI data and main dataset
    svi_df = pd.read_csv(svi_file)
    main_df = pd.read_csv(main_file)

    # Convert date columns to datetime format
    svi_df["date"] = pd.to_datetime(svi_df["date"])
    main_df["date"] = pd.to_datetime(main_df["date"])

    # Merge the datasets on date and ticker
    merged_df = pd.merge(main_df, svi_df, on=["date", "ticker"], how="left")

    # Save the merged DataFrame to CSV
    merged_df.to_csv(output_file, index=False)
    print(f"Merged data saved to: {output_file}")

if __name__ == "__main__":
    print("\nStart merging Google Trends SVI data with main dataset...\n")
    svi_file = os.path.join(INTERIM_DATA_PATH, "google_trends/google_trends_svi.csv")
    main_file = os.path.join(PROCESSED_DATA_PATH, "main.csv")
    output_file = os.path.join(PROCESSED_DATA_PATH, "main_with_svi.csv")
    merge_svi_data(svi_file, main_file, output_file)
    print("\nGoogle Trends SVI data merged with main dataset successfully!\n")

