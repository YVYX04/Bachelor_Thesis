"""
01_CRSP_cleaning.py

Script for cleaning the CRSP data for the bachelor thesis.
This file contains the functions and procedures to clean and preprocess the CRSP data.

© 2026 Yvan Richard, University of St. Gallen
"""

# Importing necessary libraries
import pandas as pd
import numpy as np
import os
import warnings

# Importing configuration
from src.config import CRSP_DATA_RAW_PATH, CRSP_DATA_INTERIM_PATH, CRSP_DATA_PROCESSED_PATH, CRSP_COLUMNS_001

def clean_crsp_data(output_name: str):
    """
    Function to clean the CRSP data.
    This function reads the raw CRSP data, performs cleaning and preprocessing steps,
    and saves the cleaned data to the interim directory.

    Args:
        output_name (str): Name of the output CSV file without extension.
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
   # crsp_data = crsp_data[crsp_data['shrcd'].isin([10, 11])]

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

    # print summary statistics of the ret variable
    print("Summary statistics of the 'ret' variable:")
    print(crsp_data['ret'].describe())

    # save the cleaned data to the interim directory
    crsp_data['ret'] = pd.to_numeric(crsp_data['ret'], errors='coerce')
    crsp_data.to_csv(os.path.join(CRSP_DATA_INTERIM_PATH, f"{output_name}.csv"), index=False)


if __name__ == "__main__":
    output_name = input("Enter the name of the output file (without extension): ")
    clean_crsp_data(output_name)
