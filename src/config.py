"""
00_config.py

Configuration file for the data of the bachelor thesis.
This file contains the paths to the data and the output directories.

© 2026 Yvan Richard, University of St. Gallen
"""

# General paths (from the root of the project)
################
# processed data paths
RAW_DATA_PATH = "data/raw/"
INTERIM_DATA_PATH = "data/interim/"
PROCESSED_DATA_PATH = "data/processed/"

# CRSP 
#######

# CRSP data paths
CRSP_DATA_RAW_PATH = "data/raw/CRSP_18_20_2.csv"
CRSP_DATA_INTERIM_PATH = "data/interim/"
CRSP_DATA_PROCESSED_PATH = "data/processed/"

# CRSP column names (Selection 001)
CRSP_COLUMNS_001 = {
    "PERMNO": "permno",
    "date": "date",
    "RET": "ret",
    "PRC": "prc",
    "VOL": "vol",
    "SHROUT": "shrout",
    "DLRET": "dlret",
    "DLSTCD": "dlstcd",
    "EXCHCD": "exchcd",
    "TICKER": "ticker",
    "SHRCD": "shrcd"
}


# Fama-French 5-factor data
############################

# Fama-French 5-factor data paths
FF_5F_DATA_RAW_PATH = "data/raw/5_factors_raw.csv"
FF_5F_DATA_INTERIM_PATH = "data/interim/"
FF_5F_DATA_PROCESSED_PATH = "data/processed/"

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

# Robintrack Data
##################

# Robintrack data paths
ROBINTRACK_DATA_RAW_PATH = "data/raw/tmp/popularity_export/"
ROBINTRACK_DATA_INTERIM_PATH = "data/interim/robintrack/"
ROBINTRACK_DATA_PROCESSED_PATH = "data/processed/robintrack/"


# Google Trends Data
#######################

# data paths for merged RH and CRSP data
CRSP_RH_MERGED_DATA_PATH = "data/processed/CRSP_RH_merged.csv"
GT_INTERIM_PATH = "data/interim/google_trends/"
GT_PROCESSED_PATH = "data/processed/google_trends/"

# data paths for raw .dta files
TSSVI_RAW_PATH = "data/google_svi/"
TSSVI_INTERIM_PATH = "data/interim/google_trends/"
TSSVI_PROCESSED_PATH = "data/processed/google_trends/"


# TAQ Data
##################

# column names for TAQ data
TAQ_COLUMNS = {
    "DATE": "date",
    "SYM_ROOT": "symro",
    "SYM_SUFFIX": "symsu",
    "symbol": "ticker",
    "BuyNumTrades_LR": "buy_num_trades_LR",
    "SellNumTrades_LR": "sell_num_trades_LR",
    "total_trade": "total_trade_LR",
    "BuyVol_LR": "buy_vol_LR",
    "SellVol_LR": "sell_vol_LR",
    "total_vol": "total_vol_LR",
    "CPrc": "close_price",
    "OPrc": "open_price",
    "CSize": "close_vol",
    "OSize": "open_vol",
    "total_vol_m": "total_vol_m", # total trade volume during market hours
    "ret_mkt_m": "intra_ret",
    "BuyNumTrades_tick": "buy_num_trades_tick",
    "SellNumTrades_tick": "sell_num_trades_tick",
    "BuyVol_tick": "buy_vol_tick",
    "SellVol_tick": "sell_vol_tick",
    "total_trade_tick": "total_trade_tick",
    "BuyNumTrades_wrds": "buy_num_trades_wrds",
    "SellNumTrades_wrds": "sell_num_trades_wrds",
    "BuyVol_wrds": "buy_vol_wrds",
    "SellVol_wrds": "sell_vol_wrds",
    "total_trade_wrds": "total_trade_wrds",
    "bs_ratio_num": "bs_ratio_num", # absolute percent order imbalance based on number of trades
    "bs_ratio_vol": "bs_ratio_vol", # absolute percent order imbalance based on volume
    "BuyNumTrades_Retail": "buy_num_trades_retail",
    "SellNumTrades_Retail": "sell_num_trades_retail",
    "BuyVol_Retail": "buy_vol_retail",
    "SellVol_Retail": "sell_vol_retail",
    "total_trade_retail": "total_trade_retail",
    "total_vol_retail": "total_vol_retail",
    "bs_ratio_retail_vol": "bs_ratio_retail_vol", # absolute percent order imbalance based on retail volume
    "bs_ratio_retail_num": "bs_ratio_retail_num", # absolute percent order imbalance based on retail number of trades
    "ivol_t": "intra_volatility",
    "BuyNumTrades_Inst50k": "buy_num_trades_inst50k",
    "SellNumTrades_Inst50k": "sell_num_trades_inst50k",
    "BuyVol_Inst50k": "buy_vol_inst50k",
    "SellVol_Inst50k": "sell_vol_inst50k",
    "total_trade_Inst50k": "total_trade_inst50k",
    "total_vol_Inst50k": "total_vol_inst50k",
    "bs_ratio_Inst50k_vol": "bs_ratio_inst50k_vol", # absolute percent order imbalance based on institutional volume
    "bs_ratio_Inst50k_num": "bs_ratio_inst50k_num" # absolute percent order imbalance based on institutional number of trades
}