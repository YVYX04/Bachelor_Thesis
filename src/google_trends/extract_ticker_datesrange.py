"""
extract_ticker_datesrange.py
Script for extracting the ticker and date range from the Google Trends data for the bachelor thesis.
This file contains the functions and procedures to extract the ticker and date range from the Google Trends data.

© 2026 Yvan Richard, University of St. Gallen
"""

# import the configuration
from src.config import CRSP_RH_MERGED_DATA_PATH, GT_INTERIM_PATH

# import necessary libraries
import pandas as pd
import os
import warnings
import numpy as np

def extract_ticker_datesrange():
    """
    Function to extract the ticker and date range from the Google Trends data.
    This function reads the merged CRSP and Robintrack data, extracts the unique tickers and the date range,
    and saves the results to a text file in the processed directory.

    The target is a data set like this:
    ticker,date_start,date_end
    AAPL,2018-05-01,2020-12-31
    """
    # 1. read the merged CRSP and Robintrack data
    merged_df = pd.read_csv(CRSP_RH_MERGED_DATA_PATH)

    # 2. extract the unique tickers and the date range for each ticker
    tickers = merged_df['ticker'].unique()
    results = []
    for ticker in tickers:
        df_ticker = merged_df[merged_df['ticker'] == ticker]
        date_start = df_ticker['date'].min()
        date_end = df_ticker['date'].max()
        results.append({'ticker': ticker, 'date_start': date_start, 'date_end': date_end})

    # 3. save the results to a .csv file in the interim directory
    results_df = pd.DataFrame(results)
    os.makedirs(GT_INTERIM_PATH, exist_ok=True)
    results_df.to_csv(os.path.join(GT_INTERIM_PATH, 'ticker_datesrange.csv'), index=False)

if __name__ == "__main__":
    print("\nExtracting ticker and date range from the merged CRSP and Robintrack data...\n")
    extract_ticker_datesrange()
    print("\nTicker and date range extracted successfully!\n")

