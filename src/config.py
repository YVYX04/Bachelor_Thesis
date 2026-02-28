"""
00_config.py

Configuration file for the data of the bachelor thesis.
This file contains the paths to the data and the output directories.

© 2026 Yvan Richard, University of St. Gallen
"""

# CRSP 
#######

# CRSP data paths
CRSP_DATA_RAW_PATH = "../data/raw/CRSP_2012_2019.csv"
CRSP_DATA_INTERIM_PATH = "../data/interim/"
CRSP_DATA_PROCESSED_PATH = "../data/processed/"

# CRSP column names (Selection 001)
CRSP_COLUMNS_001 = {
    "PERMNO": "permno",
    "date": "date",
    "RET": "ret",
    "PRC": "prc",
    "VOL": "vol",
    "SHROUT": "shrout",
    "RET": "ret",
    "DLRET": "dlret",
    "DLSTCD": "dlstcd",
    "EXCHCD": "exchcd",
    "TICKER": "ticker",
    "SHRCD": "shrcd"
}


# Fama-French 5-factor data
############################

# Fama-French 5-factor data paths
FF_5F_DATA_RAW_PATH = "../data/raw/5_factors_raw.csv"
FF_5F_DATA_INTERIM_PATH = "../data/interim/"
FF_5F_DATA_PROCESSED_PATH = "../data/processed/"

# Fama-French 5-factor column names
FF_5F_COLUMNS = {
    "date": "date",
    "Mkt-RF": "mkt_rf",
    "SMB": "smb",
    "HML": "hml",
    "RMW": "rmw",
    "CMA": "cma",
    "RF": "rf"
}

