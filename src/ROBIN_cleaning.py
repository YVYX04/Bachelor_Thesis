"""
ROBIN_cleaning.py

Script for cleaning the Robintrack data for the bachelor thesis.
This file contains the functions and procedures to clean and preprocess the Robintrack data.

© 2026 Yvan Richard, University of St. Gallen
"""

# Importing necessary libraries
import pandas as pd
import numpy as np
import os
import warnings

# Importing configuration
from config import ROBINTRACK_DATA_RAW_PATH, ROBINTRACK_DATA_INTERIM_PATH, ROBINTRACK_DATA_PROCESSED_PATH

def clean_robintrack_data():
    """
    Function to clean the Robintrack data.
    This function reads the raw Robintrack data, performs cleaning and preprocessing steps,
    and saves the cleaned data to the interim directory.
    """
    # 1) [ticker].csv are in the raw directory. We need to read all of them and concatenate them into a single DataFrame.
    # 1.1) Establish a list of all the tickers (i.e., the file names without the .csv extension) in the raw directory
    tickers = [
        os.path.splitext(f)[0]
        for f in os.listdir(ROBINTRACK_DATA_RAW_PATH)
        if f.endswith(".csv")
    ]
    N = len(tickers)
    print(f"Found {N} tickers in the raw directory.\n")

    # tickers manually removed _OUT, _PRN, MTL-, PKD~ according to Welch_2022

    # 2) Proceed ticker by ticker
    # 2.1) compute users_close and users_last for each day (i.e. last registered number of users at 4 pm ET and last count for the day, respectively)
    """
    The typical structure of the raw data is as follows:
    timestamp,users_holding
    "2018-05-02 04:52:30",16

    This means that for each day, I need to record
        (i) the last registered number of users before 4 pm ET (users_close)
        (ii) the last registered number of users for the day (users_last)

    The cleaning steps are as follows:
    1) Read the raw data for each ticker
    2) Convert the timestamp to datetime format and set it as the index
    3) Resample the data to daily frequency, taking the last value of users_holding for each day (this will give us users_last)
    4) For users_close, we need to take the last value of users_holding before 4 pm ET for each day.
    5) the cleaned data format at this stage will be
    date,users_close,users_last
    6) Save the cleaned data to the interim directory with the same file name (i.e., [ticker].csv)
    """
    i = 0
    for ticker in tickers:

        # 1) Read the raw data for the ticker
        df = pd.read_csv(os.path.join(ROBINTRACK_DATA_RAW_PATH, f"{ticker}.csv"))

        # 2) Convert the timestamp to datetime format
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d %H:%M:%S")

        # Welch (2022) restrictions
        ###########################

        # convert the timestamp from UTC to ET (Eastern Time)
        df["timestamp"] = df["timestamp"].dt.tz_localize("UTC").dt.tz_convert("America/New_York")

        # remove 45 minutes to address the lag in the data collection (as mentioned in Welch_2022)
        df["timestamp"] = df["timestamp"] - pd.Timedelta(minutes=45)

        # exculde observations in May 2018 (as mentioned in Welch_2022)
        # the sample therefore starts on June 1, 2018 in Eastern Time
        cutoff = pd.Timestamp("2018-06-01", tz="America/New_York")
        df = df[df["timestamp"] >= cutoff]

        # keep only common stocks as in CRSP (share code 10 and 11) as in Welch (2022)
        # this is done by checking the share code in the CRSP data and keeping only the tickers that correspond to common stocks
        # we will do this step later when we merge the Robintrack data with the CRSP data, as we need to keep the tickers that are in
        # the CRSP data to be able to merge them later

        # set the timestamp as the index for daily resampling
        df = df.set_index("timestamp")

        # 3) Resample the data to daily frequency, taking the last value of users_holding for each day (this will give us users_last)
        df_daily = df.resample("D").last()
        df_daily.rename(columns={"users_holding": "users_last"}, inplace=True)

        # 4) For users_close, we need to take the last value of users_holding before 4 pm ET for each day.
        df_close = df[df.index.time < pd.to_datetime("16:00:00").time()].resample("D").last()
        df_close.rename(columns={"users_holding": "users_close"}, inplace=True)

        # 5) Merge the two DataFrames on the date index
        df_cleaned = pd.merge(
            df_close[["users_close"]],
            df_daily[["users_last"]],
            left_index=True,
            right_index=True,
            how="outer",
        )
        df_cleaned.reset_index(inplace=True)
        df_cleaned.rename(columns={"timestamp": "date"}, inplace=True)
        df_cleaned["date"] = df_cleaned["date"].dt.tz_localize(None).dt.date

        # 6) Save the cleaned data to the interim directory with the same file name (i.e., [ticker].csv)
        df_cleaned.to_csv(os.path.join(ROBINTRACK_DATA_INTERIM_PATH, f"{ticker}.csv"), index=False)
        i += 1

        # progression update (in percentage)
        if i % 10 == 0 or i == N:
            progress_pct = 100 * i / N
            print(f"\rProcessing {i}/{N} ({progress_pct:5.1f}%) - {ticker}", end="", flush=True)

    return

def merge_cleaned_robintrack_data():
    """
    Function to merge all the cleaned Robintrack data into a single DataFrame and save it to the processed directory.
    This function reads all the cleaned data from the interim directory, merges them into a single DataFrame,
    and saves the merged data to the processed directory.
    """
    # 1) Read all the cleaned data from the interim directory
    tickers = [
        os.path.splitext(f)[0]
        for f in os.listdir(ROBINTRACK_DATA_INTERIM_PATH)
        if f.endswith(".csv")
    ]
    N = len(tickers)
    print(f"\nFound {N} cleaned tickers in the interim directory.\n")

    # 2) Merge all the cleaned data into a single DataFrame
    df_merged = pd.DataFrame()

    """
    The format of the final merged DataFrame should be as follows (long format):
    date,ticker,users_close,users_last

    This means that for each date, we will have one row per ticker with the corresponding users_close and users_last values.
    """

    # Proceed ticker by ticker (skip _OUT, _PRN, MTL-, and PKD~)
    i = 0
    for ticker in tickers:
        if ticker.endswith("_OUT") or ticker.endswith("_PRN") or ticker.endswith("MTL-") or ticker.endswith("PKD~"):
            continue
        # Read the cleaned data for the ticker
        df = pd.read_csv(os.path.join(ROBINTRACK_DATA_INTERIM_PATH, f"{ticker}.csv"))

        # Add a column for the ticker
        df["ticker"] = ticker

        # Append the data to the merged DataFrame
        df_merged = pd.concat([df_merged, df], ignore_index=True)

        i += 1

        # progression update (in percentage)
        if i % 10 == 0 or i == N:
            progress_pct = 100 * i / N
            print(f"\rMerging {i}/{N} ({progress_pct:5.1f}%) - {ticker}", end="", flush=True)

    # 3) Save the merged data to the processed directory
    df_merged.to_csv(os.path.join(ROBINTRACK_DATA_PROCESSED_PATH, "robintrack_merged.csv"), index=False)

    return

# execute
if __name__ == "__main__":
    # first step: interim directory
    print("\nStep 1: Extracting raw data\n")
    clean_robintrack_data()

    # second step: merge all the cleaned data into a single DataFrame and save it to the processed directory
    print("\nStep 2: Merging cleaned data\n")
    merge_cleaned_robintrack_data()

    # end of script
    print("\nRobintrack data cleaning completed.\n")