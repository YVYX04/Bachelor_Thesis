"""
TAQ_cleaning.py
"""

# Importing necessary libraries
import pandas as pd
import os
import warnings
import numpy as np 

# Importing configuration
from src.config import PROCESSED_DATA_PATH, RAW_DATA_PATH, INTERIM_DATA_PATH, TAQ_COLUMNS


def clean_taq_data():
    """
    Function to clean the TAQ data for the bachelor thesis.
    This function reads the raw TAQ data, selects the relevant columns, renames them, and saves the cleaned data to a .csv file in the interim directory.
    """

    # 1) Read the raw TAQ data
    taq_df = pd.read_csv(os.path.join(RAW_DATA_PATH, "taq_raw_2.csv"))

    # 2) Select the relevant columns and rename them according to TAQ_COLUMNS
    taq_df = taq_df[list(TAQ_COLUMNS.keys())]
    taq_df.rename(columns=TAQ_COLUMNS, inplace=True)

    # 3) Save the cleaned data to a .csv file in the interim directory
    taq_df.to_csv(os.path.join(INTERIM_DATA_PATH, "TAQ_cleaned.csv"), index=False)

if __name__ == "__main__":
    print("\nCleaning TAQ data...\n")
    clean_taq_data()
    print("\nTAQ data cleaned successfully!\n")

