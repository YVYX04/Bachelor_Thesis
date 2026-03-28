"""
RH_intraday_cleaning.py

The purpose of this script is to clean Robintrack data and construct:
- users_close: last observed user count before 4 pm ET and after 2 pm ET
- users_start: first observed user count after 10 am ET
- intraday_userchg: users_close - users_start
- users_last: last observed user count of the day

© 2026 Yvan Richard, University of St. Gallen
"""

# Importing necessary libraries
import pandas as pd
import os

# Importing configuration
from src.config import (
    ROBINTRACK_DATA_RAW_PATH,
    ROBINTRACK_DATA_INTERIM_PATH,
    ROBINTRACK_DATA_PROCESSED_PATH
)


def clean_robintrack_data():
    """
    Read each raw Robintrack ticker file, clean timestamps, construct daily variables,
    and save one cleaned file per ticker to the interim directory.
    """

    # 1) Collect ticker file names
    tickers = [
        os.path.splitext(f)[0]
        for f in os.listdir(ROBINTRACK_DATA_RAW_PATH)
        if f.endswith(".csv")
    ]
    N = len(tickers)
    print(f"Found {N} tickers in the raw directory.\n")

    i = 0
    for ticker in tickers:

        # Read raw data
        df = pd.read_csv(os.path.join(ROBINTRACK_DATA_RAW_PATH, f"{ticker}.csv"))

        # Parse timestamp
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="%Y-%m-%d %H:%M:%S")

        # Convert from UTC to ET
        df["timestamp"] = (
            df["timestamp"]
            .dt.tz_localize("UTC")
            .dt.tz_convert("America/New_York")
        )

        # Adjust for Robintrack lag (Welch-style correction)
        df["timestamp"] = df["timestamp"] - pd.Timedelta(minutes=45)

        # Sort and index by corrected timestamp
        df = df.sort_values("timestamp").set_index("timestamp")

        # ------------------------------------------------------------
        # Daily variable construction
        # ------------------------------------------------------------

        # users_close:
        # last observed user count before 4 pm ET and after 2 pm ET
        df_close = df[
            (df.index.time >= pd.to_datetime("14:00:00").time()) &
            (df.index.time <  pd.to_datetime("16:00:00").time())
        ].resample("D").last()
        df_close.rename(columns={"users_holding": "users_close"}, inplace=True)

        # users_start:
        # first observed user count after 10 am ET
        # This is our operational proxy for the first timestamp that excludes market-open trades.
        df_start = df[
            df.index.time >= pd.to_datetime("10:00:00").time()
        ].resample("D").first()
        df_start.rename(columns={"users_holding": "users_start"}, inplace=True)

        # users_last:
        # last observed user count of the day, for descriptive purposes
        df_last = df.resample("D").last()
        df_last.rename(columns={"users_holding": "users_last"}, inplace=True)

        # Merge constructed variables
        df_cleaned = pd.merge(
            df_close[["users_close"]],
            df_start[["users_start"]],
            left_index=True,
            right_index=True,
            how="outer"
        )

        df_cleaned = pd.merge(
            df_cleaned,
            df_last[["users_last"]],
            left_index=True,
            right_index=True,
            how="outer"
        )

        # Reset index and rename date column
        df_cleaned.reset_index(inplace=True)
        df_cleaned.rename(columns={"timestamp": "date"}, inplace=True)

        # Remove timezone and normalize to daily date
        df_cleaned["date"] = (
            pd.to_datetime(df_cleaned["date"])
            .dt.tz_localize(None)
            .dt.normalize()
        )

        # Intraday user change:
        # change from first timestamp that excludes market-open trading
        # to the last timestamp before market close
        df_cleaned["intraday_userchg"] = (
            df_cleaned["users_close"] - df_cleaned["users_start"]
        )

        # Save ticker-level cleaned data
        df_cleaned.to_csv(
            os.path.join(ROBINTRACK_DATA_INTERIM_PATH, f"{ticker}.csv"),
            index=False
        )

        i += 1
        if i % 10 == 0 or i == N:
            progress_pct = 100 * i / N
            print(f"\rProcessing {i}/{N} ({progress_pct:5.1f}%) - {ticker}", end="", flush=True)

    print()
    return


def merge_cleaned_robintrack_data():
    """
    Merge all cleaned ticker-level Robintrack files into one long file.
    """

    tickers = [
        os.path.splitext(f)[0]
        for f in os.listdir(ROBINTRACK_DATA_INTERIM_PATH)
        if f.endswith(".csv")
    ]
    N = len(tickers)
    print(f"\nFound {N} cleaned tickers in the interim directory.\n")

    df_merged = pd.DataFrame()
    i = 0

    for ticker in tickers:
        # skip wrong tickers
        if ticker.endswith("_OUT") or ticker.endswith("_PRN") or ticker.endswith("MTL-") or ticker.endswith("PKD~"):
            continue

        df = pd.read_csv(os.path.join(ROBINTRACK_DATA_INTERIM_PATH, f"{ticker}.csv"))
        df["ticker"] = ticker
        df_merged = pd.concat([df_merged, df], ignore_index=True)

        i += 1
        if i % 10 == 0 or i == N:
            progress_pct = 100 * i / N
            print(f"\rMerging {i}/{N} ({progress_pct:5.1f}%) - {ticker}", end="", flush=True)

    df_merged.to_csv(
        os.path.join(ROBINTRACK_DATA_PROCESSED_PATH, "robintrack_merged.csv"),
        index=False
    )

    print()
    return


if __name__ == "__main__":
    print("\nStep 1: Extracting raw data\n")
    clean_robintrack_data()

    print("\nStep 2: Merging cleaned data\n")
    merge_cleaned_robintrack_data()

    print("\nRobintrack data cleaning completed.\n")