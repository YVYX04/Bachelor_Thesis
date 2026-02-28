"""
5F_cleaning.py

Script for cleaning the Fama-French 5-factor data for the bachelor thesis.
This file contains the functions and procedures to clean and preprocess the Fama-French 5-factor data.

© 2026 Yvan Richard, University of St. Gallen
"""

# Importing necessary libraries
import pandas as pd
import numpy as np
import os
import warnings

# import configuration
from config import FF_5F_DATA_RAW_PATH, FF_5F_DATA_INTERIM_PATH, FF_5F_DATA_PROCESSED_PATH, FF_5F_COLUMNS


def clean_fama_french_5f_data():
    """
    Function to clean the Fama-French 5-factor data.
    This function reads the raw Fama-French 5-factor data, performs cleaning and preprocessing steps,
    and saves the cleaned data to the interim directory.
    """
    # Read the raw Fama-French 5-factor data
    data = pd.read_csv(FF_5F_DATA_RAW_PATH, skiprows=4)

    # drop last 3 rows (contains only footnotes)
    data.drop(index=data.index[-3:], inplace=True)

    # first column is not named but is the date, so we name it 'date'
    data.rename(columns={data.columns[0]: 'date'}, inplace=True)

    # parse date column to datetime
    data['date'] = pd.to_datetime(data['date'], format='%Y%m%d')

    # only keep data from 2012 to 2019
    data = data[(data['date'].dt.year >= 2012) & (data['date'].dt.year <= 2019)]

    # rename columns according to config
    data.rename(columns=FF_5F_COLUMNS, inplace=True)

    # check that all columns except date are numeric, and if not, convert them to numeric (coercing errors to NaN)
    for column in data.columns:
        if column != 'date':
            if not pd.api.types.is_numeric_dtype(data[column]):
                data[column] = pd.to_numeric(data[column], errors='coerce')

    # check for missing values
    for column in data.columns:
        if data[column].isnull().any():
            warnings.warn(f"Column {column} contains missing values.\n")

            # compute the percentage of missing values
            missing_percentage = data[column].isnull().mean() * 100
            print(f"Percentage of missing values in column {column}: {missing_percentage:.2f}%\n")

    # save cleaned data to interim directory
    data.to_csv(os.path.join(FF_5F_DATA_INTERIM_PATH, f"{output_name}.csv"), index=False)

if __name__ == "__main__":
    output_name = input("Enter the name of the output file (without extension): ")
    clean_fama_french_5f_data()
    