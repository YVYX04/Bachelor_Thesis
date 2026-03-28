"""
01_CRSP_cleaning.py

Script for cleaning the CRSP data for the bachelor thesis.
This file contains the functions and procedures to clean and preprocess the CRSP data.

© 2026 Yvan Richard, University of St. Gallen
"""

# Importing necessary libraries
from pathlib import Path
import pandas as pd
import numpy as np
import os
import warnings

# Importing configuration
from src.config import CRSP_DATA_RAW_PATH, CRSP_DATA_INTERIM_PATH, CRSP_DATA_PROCESSED_PATH, CRSP_COLUMNS_001

def clean_crsp_data(output_name: str, deduplicate_ticker_date: bool = True):
    """
    Clean the CRSP data and optionally collapse duplicate ticker-date observations.

    The duplicate collapse is intended for downstream merges performed on (ticker, date),
    such as the Robintrack merge used in the thesis. When multiple CRSP securities share
    the same ticker on the same date, the function keeps the observation with the largest
    market capitalization proxy |prc| * shrout.

    Args:
        output_name (str): Name of the output CSV file without extension.
        deduplicate_ticker_date (bool): If True, keep a single observation per (ticker, date)
            using the largest market-cap proxy. The full cleaned file before this collapse is
            also saved for audit purposes.
    """
    # Read the raw CRSP data
    # Use low_memory=False to avoid chunk-wise dtype inference warnings on large files
    # Read potentially mixed-type columns as strings; we'll coerce them later.
    crsp_data = pd.read_csv(
        CRSP_DATA_RAW_PATH,
        low_memory=False,
        dtype={"ret": "string", "dlret": "string", "dlstcd": "float", "shrcd": "float", "exchcd": "float"},
    )

    # Select relevant columns and rename them
    crsp_data = crsp_data[list(CRSP_COLUMNS_001.keys())]
    crsp_data.rename(columns=CRSP_COLUMNS_001, inplace=True)

    # Convert date column to datetime format
    crsp_data['date'] = pd.to_datetime(crsp_data['date'], format='%Y-%m-%d')

    # select only common stocks (shrcd = 10 or 11)
    # Barber et al. (2022) do not apply this filter! (I imitate their design)
    crsp_data = crsp_data[crsp_data['shrcd'].isin([10, 11])]

    # select only stocks listed on NYSE, AMEX, NASDAQ (exchcd = 1, 2, 3)
    # Barber et al. (2022) do not apply this filter! (I imitate their design)
    # crsp_data = crsp_data[crsp_data['exchcd'].isin([1, 2, 3])]

    # clean the returns (ret) and adjust for delisting returns (dlret, dlstcd)
    crsp_data['ret'] = crsp_data['ret'].replace(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                                                 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], np.nan)
    crsp_data['dlret'] = crsp_data['dlret'].replace(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                                                     'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'], np.nan)

    crsp_data['ret'] = pd.to_numeric(crsp_data['ret'], errors='coerce')
    crsp_data['dlret'] = pd.to_numeric(crsp_data['dlret'], errors='coerce')

    # Default imputation for delisting returns when dlret is missing
    # If dlstcd is present, use -1 by default; for specific poor-performance delisting codes use -0.3.
    default_dlret = pd.Series(np.nan, index=crsp_data.index, dtype='float64')

    mask_1 = crsp_data['dlstcd'].notna()
    default_dlret.loc[mask_1] = -1.0

    codes = [500, 520, 574, 580, 584] + list(range(551, 574))
    mask_2 = crsp_data['dlstcd'].isin(codes)
    default_dlret.loc[mask_2] = -0.3

    # Fill missing dlret with the default imputation
    crsp_data['dlret'] = crsp_data['dlret'].fillna(default_dlret)

    # If both ret and dlret exist, combine them multiplicatively.
    # If ret is missing but dlret exists, use dlret.
    mask_both = crsp_data['ret'].notna() & crsp_data['dlret'].notna()
    crsp_data.loc[mask_both, 'ret'] = (
        (1 + crsp_data.loc[mask_both, 'ret']) * (1 + crsp_data.loc[mask_both, 'dlret']) - 1
    )

    mask_ret_missing = crsp_data['ret'].isna() & crsp_data['dlret'].notna()
    crsp_data.loc[mask_ret_missing, 'ret'] = crsp_data.loc[mask_ret_missing, 'dlret']

    # Drop observations with unavailable returns after cleaning
    # Report number of observations dropped due to missing returns
    missing_returns = crsp_data['ret'].isna().sum()
    if missing_returns > 0:
        warnings.warn(f"{missing_returns} observations with missing returns will be dropped.", category=UserWarning)
    crsp_data.dropna(subset=['ret'], inplace=True)

    # step 6: sanity check: ensure that there are no returns less than -1
    negative_returns = crsp_data[crsp_data['ret'] < -1].shape[0]
    if negative_returns > 0:
        raise ValueError(f"Error: There are {negative_returns} returns less than -1 in the 'ret' variable.")
    
    # check for missing values in the prc, vol, and shrout columns
    # the presence of missing values in these columns can lead to issues in the calculation
    # of the market capitalization and other variables, and can also indicate data quality issues.
    # However, instead of dropping the rows with missing values, I prefer to raise a warning to
    # alert the user about the presence of missing values in these columns.
    missing_prc = crsp_data['prc'].isna().sum()
    missing_vol = crsp_data['vol'].isna().sum()
    missing_shrout = crsp_data['shrout'].isna().sum()
    if missing_prc > 0 or missing_vol > 0 or missing_shrout > 0:
        warnings.warn(
            "Missing values detected in 'prc', 'vol', or 'shrout'. "
            f"Missing prc: {missing_prc}, missing vol: {missing_vol}, missing shrout: {missing_shrout}.",
            category=UserWarning,
        )

    # volume missing usually means no reported trading volume; set to 0 rather than dropping observations.
    if missing_vol > 0:
        crsp_data['vol'] = crsp_data['vol'].fillna(0)
    
    # columns to keep in the final dataset
    crsp_data = crsp_data[['permno', 'date', 'ret', 'prc', 'vol', 'shrout', 'ticker', 'exchcd']]

    # Ensure numeric types needed for duplicate diagnostics and the market-cap proxy.
    for col in ['prc', 'vol', 'shrout']:
        crsp_data[col] = pd.to_numeric(crsp_data[col], errors='coerce')

    # Keep an audit copy before collapsing duplicate (ticker, date) observations.
    crsp_data_full = crsp_data.copy()

    # Diagnose duplicate ticker-date observations.
    ticker_date_counts = (
        crsp_data.groupby(['date', 'ticker'])
        .size()
        .reset_index(name='n_rows')
    )
    duplicated_pairs = ticker_date_counts[ticker_date_counts['n_rows'] > 1].copy()

    if not duplicated_pairs.empty:
        warnings.warn(
            f"Detected {len(duplicated_pairs)} duplicated (date, ticker) pairs in CRSP. "
            "This usually reflects multiple permnos sharing the same ticker on a given date.",
            category=UserWarning,
        )

    if deduplicate_ticker_date:
        # When the downstream merge uses (ticker, date), retain a single CRSP row per pair.
        # The economically dominant security is proxied by the largest absolute market cap.
        crsp_data['mktcap_proxy'] = crsp_data['prc'].abs() * crsp_data['shrout']

        dup_rows_before = crsp_data.duplicated(subset=['date', 'ticker'], keep=False).sum()
        if dup_rows_before > 0:
            crsp_data = (
                crsp_data.sort_values(
                    ['date', 'ticker', 'mktcap_proxy', 'permno'],
                    ascending=[True, True, False, True]
                )
                .drop_duplicates(subset=['date', 'ticker'], keep='first')
                .copy()
            )

            warnings.warn(
                f"Collapsed {dup_rows_before} duplicated CRSP rows to a unique (date, ticker) sample "
                "by keeping the row with the largest market-cap proxy.",
                category=UserWarning,
            )

        if crsp_data.duplicated(subset=['date', 'ticker']).any():
            raise ValueError("CRSP data are still not unique at the (date, ticker) level after deduplication.")

        crsp_data.drop(columns=['mktcap_proxy'], inplace=True)

    # print summary statistics of the ret variable
    print("Summary statistics of the 'ret' variable:")
    print(crsp_data['ret'].describe())

    # save the cleaned data to the interim directory
    crsp_data['ret'] = pd.to_numeric(crsp_data['ret'], errors='coerce')

    output_path = Path(CRSP_DATA_INTERIM_PATH) / f"{output_name}.csv"
    crsp_data.to_csv(output_path, index=False)

    # Also save the full cleaned file before ticker-date deduplication for audit/debugging.
    if deduplicate_ticker_date:
        full_output_path = Path(CRSP_DATA_INTERIM_PATH) / f"{output_name}_full_before_ticker_date_dedup.csv"
        crsp_data_full.to_csv(full_output_path, index=False)

    print(f"Saved cleaned CRSP data to: {output_path}")


if __name__ == "__main__":
    output_name = input("Enter the name of the output file (without extension): ")
    clean_crsp_data(output_name, deduplicate_ticker_date=True)
