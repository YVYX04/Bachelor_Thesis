"""
herding_events.py

In this file, I define the functions to identify herding events in the data for the bachelor thesis.
The main function is identify_herding_events(), which identifies herding events in the data and
saves the results to a .csv file in the processed directory. I reproduce the methodology used
by Barbet et al. (2022) to identify herding events in the data.

Here is an excerpt from the paper describing the methodology to identify herding events:
"While we find that user changes are generally small, a number of extreme
user change events are in our sample. These extreme events likely occur
because Robinhood users are new to markets and more willing to specu-
late. These extreme events are also likely a good proxy for the behavior
of investors who are unduly influenced by attention-grabbing events. To
identify Robinhood herding events, we first identify stocks with an increase
in users (i.e., userratio(t) > 1) and at least 100 users entering the day (i.e.,
users_close(t-1) ≥ 100). We then sort these stocks based on the day t userratio
and identify the top 0.5% of stocks as Robinhood herding stocks, which we de-
note with the indicator variable rh_herd. This procedure results in a sample of
4,884 herding events (about nine per day on average) for 2,301 unique tickers.
"""

# Importing necessary libraries
import pandas as pd
import os
import warnings
import numpy as np

# Importing configuration
from src.config import PROCESSED_DATA_PATH, RAW_DATA_PATH, INTERIM_DATA_PATH

def identify_herding_events():
    # 1) read the merged CRSP, Robintrack, and TAQ data
    try:
        merged_df = pd.read_csv(os.path.join(PROCESSED_DATA_PATH, "final_sample.csv"))
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    # 2) Build relevant variables
    # make sure the lag is computed in chronological order within each ticker
    merged_df["date"] = pd.to_datetime(merged_df["date"])
    merged_df = merged_df.sort_values(["ticker", "date"]).copy()

    # userratio = users_close(t) / users_close(t-1)
    merged_df["users_close_lag1"] = merged_df.groupby("ticker")["users_close"].shift(1)
    merged_df["userratio"] = merged_df["users_close"] / merged_df["users_close_lag1"]

    # flag np.inf and -np.inf values in userratio as NaN (can happen when users_close_lag1 is zero)
    merged_df["userratio"].replace([np.inf, -np.inf], np.nan, inplace=True)

    # 3) shortlist the possible herding events based on the criteria of Barbet et al. (2022)
    merged_df["shortlist_herd"] = (
        (merged_df["userratio"] > 1)
        & (merged_df["users_close_lag1"] >= 100)
        & merged_df["userratio"].notna()
    )

    # 4) Identify the top 0.5% of shortlisted stocks based on userratio for each day
    # Only shortlisted stocks can be flagged as herding events.
    merged_df["rh_herd"] = False
    merged_df.loc[merged_df["shortlist_herd"], "rh_herd"] = (
        merged_df.loc[merged_df["shortlist_herd"]]
        .groupby("date")["userratio"]
        .transform(lambda x: x >= x.quantile(0.995))
    )

    # 5) Report on the number of herding events identified, number of
    # unique tickers involved
    num_herding_events = merged_df["rh_herd"].sum()
    num_unique_tickers = merged_df.loc[merged_df["rh_herd"], "ticker"].nunique()
    print(f"Number of herding events identified: {num_herding_events}")
    print(f"Number of unique tickers involved: {num_unique_tickers}")

    # 6) Save two data frames to the processed directory: one with all stocks and a flag for herding events, and one with only the herding events
    merged_df.to_csv(os.path.join(PROCESSED_DATA_PATH, "herding_events_full.csv"), index=False)
    merged_df[merged_df["rh_herd"]].to_csv(os.path.join(PROCESSED_DATA_PATH, "herding_events_only.csv"), index=False)

if __name__ == "__main__":
    print("\nIdentifying herding events...\n")
    identify_herding_events()
    print("\nHerding events identified and saved successfully!\n")
