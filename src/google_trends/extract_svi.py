"""
extract_svi.py
Script for extracting the SVI from the Google Trends data for the bachelor thesis.
This file contains the functions and procedures to extract the SVI from the Google Trends data.

© 2026 Yvan Richard, University of St. Gallen
"""
from __future__ import annotations

# import the configuration
from src.config import GT_INTERIM_PATH, GT_PROCESSED_PATH

# import necessary libraries
import pandas as pd
import os
import warnings
import numpy as np
import time
import random
from pathlib import Path
from typing import List, Tuple
from pytrends.request import TrendReq

# ------------
# Internal Configurations
# ------------
CHUNK_DAYS = 180
OVERLAP_DAYS = 30
PADDING_DAYS = 30

SLEEP_MIN = 2.0
SLEEP_MAX = 5.0


PROCESSED_DIR = Path(GT_PROCESSED_PATH)
INPUT_FILE = Path(GT_INTERIM_PATH) / "ticker_datesrange.csv"
INTERIM_TICKER_CHUNKS_DIR = Path(GT_INTERIM_PATH) / "ticker_chunks"

FINAL_FILE = Path(GT_PROCESSED_PATH) / "google_trends_svi.csv"


# -----------------------------
# Utilities
# -----------------------------
def make_dirs() -> None:
    INPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    INTERIM_TICKER_CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def load_input(path: str) -> pd.DataFrame:
    """
    Load the input CSV file containing ticker and date information.
    
    Args:
        - path (str): Path to the input CSV file.
    
    Returns:
        - pd.DataFrame: DataFrame with normalized date and cleaned ticker columns. (just in case)
    """
    df = pd.read_csv(path)
    df["date_start"] = pd.to_datetime(df["date_start"]).dt.normalize()
    df["date_end"] = pd.to_datetime(df["date_end"]).dt.normalize()
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df = df.dropna(subset=["date_start", "date_end", "ticker"]).drop_duplicates()
    return df


def ticker_date_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add padding to the already existing per-ticker date ranges.

    Args:
        df (pd.DataFrame): DataFrame containing one row per ticker with
            columns 'ticker', 'date_start', and 'date_end'.

    Returns:
        pd.DataFrame: DataFrame with columns 'ticker', 'date_start', 'date_end',
            'start', and 'end'.
    """
    out = df[["ticker", "date_start", "date_end"]].copy()
    out["start"] = out["date_start"] - pd.Timedelta(days=PADDING_DAYS)
    out["end"] = out["date_end"] + pd.Timedelta(days=PADDING_DAYS)
    return out


def build_chunks(start: pd.Timestamp, end: pd.Timestamp,
                 chunk_days: int = CHUNK_DAYS,
                 overlap_days: int = OVERLAP_DAYS) -> List[Tuple[pd.Timestamp, pd.Timestamp]]:
    chunks = []
    cur_start = start

    while cur_start <= end:
        cur_end = min(cur_start + pd.Timedelta(days=chunk_days - 1), end)
        chunks.append((cur_start, cur_end))
        if cur_end >= end:
            break
        cur_start = cur_end - pd.Timedelta(days=overlap_days - 1)

    return chunks


def safe_sleep() -> None:
    time.sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))


def fetch_trends_chunk(pytrends: TrendReq, keyword: str,
                       start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    timeframe = f"{start.strftime('%Y-%m-%d')} {end.strftime('%Y-%m-%d')}"

    # the argument geo is set to "US" since Robinhood users are in the US.
    pytrends.build_payload([keyword], timeframe=timeframe, geo="US", gprop="")
    data = pytrends.interest_over_time()

    if data.empty:
        return pd.DataFrame(columns=["date", "value"])

    data = data.reset_index()
    data["date"] = pd.to_datetime(data["date"]).dt.normalize()

    if "isPartial" in data.columns:
        data = data.drop(columns=["isPartial"])

    data = data.rename(columns={keyword: "value"})
    return data[["date", "value"]]


def save_raw_chunk(ticker: str, idx: int, start: pd.Timestamp,
                   end: pd.Timestamp, df: pd.DataFrame) -> Path:
    fname = f"{ticker}__chunk{idx:03d}__{start:%Y%m%d}_{end:%Y%m%d}.csv"
    path = INTERIM_TICKER_CHUNKS_DIR / fname
    df.to_csv(path, index=False)
    return path


def load_raw_chunk(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"]).dt.normalize()
    return df.sort_values("date").reset_index(drop=True)


def rescale_two_chunks(prev_df: pd.DataFrame, next_df: pd.DataFrame) -> pd.DataFrame:
    """
    Rescale next_df to prev_df using the overlap period.
    Uses overlap medians over positive values.
    """
    merged = prev_df.merge(next_df, on="date", how="inner", suffixes=("_prev", "_next"))

    # keep only positive overlap values to avoid division by zero / dead overlaps
    valid = merged[(merged["value_prev"] > 0) & (merged["value_next"] > 0)].copy()

    if len(valid) == 0:
        # fallback: no scaling possible
        scale = 1.0
    else:
        prev_med = valid["value_prev"].median()
        next_med = valid["value_next"].median()
        scale = prev_med / next_med if next_med != 0 else 1.0

    out = next_df.copy()
    out["value"] = out["value"] * scale
    return out


def stitch_chunks(chunk_paths: List[Path]) -> pd.DataFrame:
    if not chunk_paths:
        return pd.DataFrame(columns=["date", "value"])

    chunk_paths = sorted(chunk_paths)
    stitched = load_raw_chunk(chunk_paths[0]).copy()
    stitched["value"] = stitched["value"].astype(float)

    for p in chunk_paths[1:]:
        nxt = load_raw_chunk(p).copy()
        nxt["value"] = nxt["value"].astype(float)
        nxt = rescale_two_chunks(stitched, nxt)

        # append only dates not yet in stitched
        nxt = nxt[~nxt["date"].isin(stitched["date"])]
        stitched = pd.concat([stitched, nxt], ignore_index=True)

    stitched = stitched.sort_values("date").reset_index(drop=True)
    return stitched


def fetch_one_ticker(ticker: str, start: pd.Timestamp, end: pd.Timestamp,
                     retries: int = 3) -> pd.DataFrame:
    pytrends = TrendReq(hl="en-US", tz=0)
    chunks = build_chunks(start, end)
    saved_paths: List[Path] = []

    for idx, (cstart, cend) in enumerate(chunks):
        success = False
        for attempt in range(retries):
            try:
                df_chunk = fetch_trends_chunk(pytrends, ticker, cstart, cend)
                save_path = save_raw_chunk(ticker, idx, cstart, cend, df_chunk)
                saved_paths.append(save_path)
                safe_sleep()
                success = True
                break
            except Exception as e:
                wait = 10 * (attempt + 1) + random.uniform(0, 3)
                print(f"[WARN] {ticker} chunk {idx} failed (attempt {attempt+1}/{retries}): {e}")
                time.sleep(wait)

        if not success:
            print(f"[ERROR] Failed for {ticker}, chunk {idx}. Skipping remaining chunks.")
            break

    stitched = stitch_chunks(saved_paths)
    if not stitched.empty:
        stitched["ticker"] = ticker
    return stitched[["date", "ticker", "value"]] if not stitched.empty else pd.DataFrame(
        columns=["date", "ticker", "value"]
    )


def main() -> None:
    make_dirs()

    df_input = load_input(INPUT_FILE)
    ranges = ticker_date_ranges(df_input)

    results = []

    for i, row in ranges.iterrows():
        ticker = row["ticker"]
        start = row["start"]
        end = row["end"]

        print(f"\r[{i+1}/{len(ranges)}] Fetching {ticker}: {start.date()} -> {end.date()}", end="", flush=True)
        ticker_df = fetch_one_ticker(ticker, start, end)

        if ticker_df.empty:
            continue

        # keep only requested dates if you want a minimal final file
        requested_start = row["date_start"]
        requested_end = row["date_end"]
        ticker_df = ticker_df[
            (ticker_df["date"] >= requested_start) & (ticker_df["date"] <= requested_end)
        ].copy()

        results.append(ticker_df)

    if results:
        final = pd.concat(results, ignore_index=True)
        final = final.rename(columns={"value": "gtrends_svi_daily"})
        final.to_csv(FINAL_FILE, index=False)
        print(f"Saved final panel to {FINAL_FILE}")
    else:
        print("No data collected.")


if __name__ == "__main__":
    main()
