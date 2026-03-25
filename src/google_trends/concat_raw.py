"""
concat_raw.py
In this script, I concatenate the three .dta files and write
the result to a single .csv file.

© 2026 Yvan Richard, University of St. Gallen
"""

# import necessary libraries
import pandas as pd
import os
import warnings
import numpy as np

# import the configuration
from src.config import TSSVI_RAW_PATH, TSSVI_INTERIM_PATH

def concat_raw():
    """
    Function to concatenate the three .dta files and write the result to a single .csv file.
    The three .dta files are located in the raw directory and have the following format:
    date,ticker,TSSVI
    2018-05-01,AAPL,0.5

    The concatenated file will be saved in the interim directory with the name "google_trends_svi.csv".
    """
    # 1) read the three .dta files and concatenate them into a single DataFrame
    df1 = pd.read_stata(os.path.join(TSSVI_RAW_PATH, "TSSVI_RUSSEL3000_2018.dta"))
    df2 = pd.read_stata(os.path.join(TSSVI_RAW_PATH, "TSSVI_RUSSEL3000_2019.dta"))
    df3 = pd.read_stata(os.path.join(TSSVI_RAW_PATH, "TSSVI_RUSSEL3000_2020.dta"))
    df4 = pd.read_stata(os.path.join(TSSVI_RAW_PATH, "TSSVI_SP500_2010_2022.dta"))

    # for each DataFrame, keep only the columns "date", "tic", and "TSSVI"
    df1 = df1[["date", "tic", "TSSVI"]]
    df2 = df2[["date", "tic", "TSSVI"]]
    df3 = df3[["date", "tic", "TSSVI"]]
    df4 = df4[["date", "tic", "TSSVI"]]

    # parse the "date" column as datetime
    df1["date"] = pd.to_datetime(df1["date"])
    df2["date"] = pd.to_datetime(df2["date"])
    df3["date"] = pd.to_datetime(df3["date"])
    df4["date"] = pd.to_datetime(df4["date"])

    # sort each DataFrame by date and ticker
    df1 = df1.sort_values(["date", "tic"]).copy()
    df2 = df2.sort_values(["date", "tic"]).copy()
    df3 = df3.sort_values(["date", "tic"]).copy()
    df4 = df4.sort_values(["date", "tic"]).copy()

    df_concat = pd.concat([df1, df2, df3, df4], ignore_index=True)

    # 2) save the concatenated DataFrame to a .csv file in the interim directory
    os.makedirs(TSSVI_INTERIM_PATH, exist_ok=True)

    # rename "tic" to "ticker"
    df_concat = df_concat.rename(columns={"tic": "ticker"})

    # clip the dates between 1st May 2018 and 31st of August 2020
    df_concat["date"] = pd.to_datetime(df_concat["date"])
    df_concat = df_concat[(df_concat["date"] >= "2018-05-01") & (df_concat["date"] <= "2020-08-31")]

    # report length of the concatenated DataFrame, number of unique tickers, and missing values
    print(f"Length of concatenated DataFrame: {len(df_concat)}")
    print(f"Number of unique tickers: {df_concat['ticker'].nunique()}")
    print(f"Missing values in 'date' column: {df_concat['date'].isnull().sum()}")
    print(f"Missing values in 'ticker' column: {df_concat['ticker'].isnull().sum()}")
    print(f"Missing values in 'TSSVI' column: {df_concat['TSSVI'].isnull().sum()}")

    # write to .csv
    df_concat.to_csv(os.path.join(TSSVI_INTERIM_PATH, "google_trends_svi.csv"), index=False)


if __name__ == "__main__":
    print("\nConcatenating raw .dta files and saving to interim directory...\n")
    concat_raw()
    print("\nRaw .dta files concatenated and saved successfully!\n")

