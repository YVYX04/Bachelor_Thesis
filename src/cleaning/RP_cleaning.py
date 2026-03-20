"""
RP_cleaning.py

This script contains functions for cleaning the raw data from RavenPack.
"""

# Import necessary libraries
import os
from collections import defaultdict

import numpy as np
import pandas as pd

# Import configuration
from src.config import RAW_DATA_PATH, INTERIM_DATA_PATH, PROCESSED_DATA_PATH, RP_COLUMNS


def _print_progress(chunk_idx, rows_processed, file_size_mb, bytes_read=None):
    """Print lightweight progress information while processing chunks."""
    msg = f"Processed chunk {chunk_idx:,} | rows: {rows_processed:,}"
    if bytes_read is not None and file_size_mb > 0:
        pct = min(100.0, 100 * bytes_read / (file_size_mb * 1024 * 1024))
        msg += f" | file progress: {pct:5.1f}%"
    print(msg)


def _merge_grouped_stats(target, grouped, key_cols=("ticker", "date")):
    """Accumulate grouped statistics from a chunk into a global dictionary."""
    for row in grouped.itertuples(index=False):
        key = tuple(getattr(row, col) for col in key_cols)
        for col, value in row._asdict().items():
            if col not in key_cols:
                target[key][col] += value


def clean_rp_data(file_path, output_name, chunksize=500_000, complete_grid=False):
    """
    Clean and aggregate RavenPack data in chunks to avoid loading the full CSV
    into memory.

    Parameters
    ----------
    file_path : str
        Path to the raw RavenPack CSV file.
    output_name : str
        Name of the output file (without extension).
    chunksize : int, optional
        Number of rows read per chunk.
    complete_grid : bool, optional
        If True, expand the final output to a full ticker-date grid. This is more
        memory intensive. By default, only observed ticker-date combinations are kept.
    """

    if not os.path.exists(file_path):
        print(f"Error: file not found -> {file_path}")
        return None

    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = file_size_bytes / (1024 * 1024)
    print(f"\nStart reading RavenPack data in chunks from: {file_path}")
    print(f"File size: {file_size_mb:,.2f} MB | chunksize: {chunksize:,}\n")

    # containers for global aggregation
    unique_tickers = set()
    num_news_dict = defaultdict(lambda: defaultdict(float))
    num_news_relevant_dict = defaultdict(lambda: defaultdict(float))
    ess_dict = defaultdict(lambda: defaultdict(float))
    css_dict = defaultdict(lambda: defaultdict(float))
    anl_chg_dict = defaultdict(lambda: defaultdict(float))

    rows_processed = 0
    bytes_read = 0

    # read only the columns needed for the aggregation
    usecols = list(RP_COLUMNS.keys())
    print(usecols)

    reader = pd.read_csv(file_path, usecols=usecols, chunksize=chunksize)

    for chunk_idx, chunk in enumerate(reader, start=1):
        original_columns = set(chunk.columns)
        rename_map = {k: v for k, v in RP_COLUMNS.items() if k in original_columns}
        if rename_map:
            chunk = chunk.rename(columns=rename_map)

        required_cols = ["ticker", "date", "story_id", "relevance", "ess", "css", "anl_chg"]
        missing_cols = [col for col in required_cols if col not in chunk.columns]
        if missing_cols:
            raise KeyError(f"Missing required columns in RavenPack chunk: {missing_cols}")

        chunk["date"] = pd.to_datetime(chunk["date"], errors="coerce").dt.normalize()
        chunk = chunk.dropna(subset=["ticker", "date"])

        unique_tickers.update(chunk["ticker"].astype(str).unique())

        # num_news: unique story_id per ticker-date
        num_news = (
            chunk.groupby(["ticker", "date"])["story_id"]
            .nunique()
            .reset_index(name="num_news")
        )
        _merge_grouped_stats(num_news_dict, num_news)

        # num_news_relevant: unique story_id with relevance > 75 per ticker-date
        relevant_chunk = chunk[chunk["relevance"] > 75]
        if not relevant_chunk.empty:
            num_news_relevant = (
                relevant_chunk.groupby(["ticker", "date"])["story_id"]
                .nunique()
                .reset_index(name="num_news_relevant")
            )
            _merge_grouped_stats(num_news_relevant_dict, num_news_relevant)

        # ess: mean within ticker-date, accumulated as sum and count across chunks
        ess_grouped = (
            chunk.groupby(["ticker", "date"])
            .agg(ess_sum=("ess", "sum"), ess_count=("ess", "count"))
            .reset_index()
        )
        _merge_grouped_stats(ess_dict, ess_grouped)

        # css: 1 / (100 * N) * sum(css_i * relevance_i)
        chunk["css_weighted"] = chunk["css"] * chunk["relevance"]
        css_grouped = (
            chunk.groupby(["ticker", "date"])
            .agg(css_weighted_sum=("css_weighted", "sum"), css_count=("css", "count"))
            .reset_index()
        )
        _merge_grouped_stats(css_dict, css_grouped)

        # anl_chg: 1 / (100 * N) * sum(anl_chg_i)
        anl_chg_grouped = (
            chunk.groupby(["ticker", "date"])
            .agg(anl_chg_sum=("anl_chg", "sum"), anl_chg_count=("anl_chg", "count"))
            .reset_index()
        )
        _merge_grouped_stats(anl_chg_dict, anl_chg_grouped)

        rows_processed += len(chunk)
        bytes_read += chunk.memory_usage(deep=True).sum()
        _print_progress(chunk_idx, rows_processed, file_size_mb, bytes_read=bytes_read)

    print(f"\nNumber of unique tickers in the RavenPack data: {len(unique_tickers):,}.\n")

    def dict_to_df(stats_dict, value_name=None, numerator=None, denominator=None):
        rows = []
        for (ticker, date), stats in stats_dict.items():
            row = {"ticker": ticker, "date": date}
            if value_name is not None:
                row[value_name] = stats[value_name]
            else:
                denom = stats[denominator]
                row[numerator] = np.nan if denom == 0 else stats[numerator] / denom
            rows.append(row)
        return pd.DataFrame(rows)

    num_news_df = dict_to_df(num_news_dict, value_name="num_news")
    num_news_relevant_df = dict_to_df(num_news_relevant_dict, value_name="num_news_relevant")

    ess_rows = []
    for (ticker, date), stats in ess_dict.items():
        ess_value = np.nan if stats["ess_count"] == 0 else stats["ess_sum"] / stats["ess_count"]
        ess_rows.append({"ticker": ticker, "date": date, "ess": ess_value})
    ess_df = pd.DataFrame(ess_rows)

    css_rows = []
    for (ticker, date), stats in css_dict.items():
        css_value = np.nan if stats["css_count"] == 0 else stats["css_weighted_sum"] / (100 * stats["css_count"])
        css_rows.append({"ticker": ticker, "date": date, "css": css_value})
    css_df = pd.DataFrame(css_rows)

    anl_chg_rows = []
    for (ticker, date), stats in anl_chg_dict.items():
        anl_chg_value = np.nan if stats["anl_chg_count"] == 0 else stats["anl_chg_sum"] / (100 * stats["anl_chg_count"])
        anl_chg_rows.append({"ticker": ticker, "date": date, "anl_chg": anl_chg_value})
    anl_chg_df = pd.DataFrame(anl_chg_rows)

    # merge all aggregates
    rp_agg_df = num_news_df.copy()
    for df in [num_news_relevant_df, ess_df, css_df, anl_chg_df]:
        if not df.empty:
            rp_agg_df = rp_agg_df.merge(df, on=["ticker", "date"], how="outer")

    rp_agg_df = rp_agg_df.sort_values(["ticker", "date"]).reset_index(drop=True)

    # optional expansion to a full ticker-date grid (can be memory intensive)
    if complete_grid:
        print("\nExpanding to the full ticker-date grid. This may take additional memory...\n")
        date_range = pd.date_range(start="2018-05-13", end="2020-08-14", freq="D")
        tickers = sorted(unique_tickers)
        full_index = pd.MultiIndex.from_product([tickers, date_range], names=["ticker", "date"])
        rp_agg_df = (
            rp_agg_df.set_index(["ticker", "date"])
            .reindex(full_index)
            .reset_index()
        )

    print("\nSummary statistics for the aggregated RavenPack data:\n")
    print(rp_agg_df.describe(include="all"))

    output_dir = os.path.join(INTERIM_DATA_PATH, "RP")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{output_name}.csv")
    rp_agg_df.to_csv(output_path, index=False)

    print(f"\nSaved cleaned RavenPack data to: {output_path}\n")
    return rp_agg_df


if __name__ == "__main__":
    print("\nStart cleaning RavenPack data...\n")
    clean_rp_data(
        os.path.join(RAW_DATA_PATH, "RP/rp_raw_10.csv"),
        "rp_cleaned_10",
        chunksize=500_000,
        complete_grid=False,
    )
    print("\nRavenPack data cleaned successfully!\n")






