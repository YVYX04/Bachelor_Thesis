from __future__ import annotations

import os
import time
import logging
from pathlib import Path
from typing import Iterable

from datetime import timedelta

import pandas as pd
import requests
from requests.auth import HTTPBasicAuth


# =========================
# Configuration
# =========================

BASE_URL = "https://api-gw-prd.stocktwits.com/api-middleware/external/sentiment/v2"

# environment variables for credentials
STOCKTWITS_USERNAME = os.getenv("STOCKTWITS_USERNAME")
STOCKTWITS_PASSWORD = os.getenv("STOCKTWITS_PASSWORD")

# default paths
INPUT_TICKERS_PATH = Path("data/interim/tickers_9007.csv")
OUTPUT_RAW_CSV_PATH = Path("data/processed/stocktwits_sentiment_raw.csv")
OUTPUT_DAILY_CSV_PATH = Path("data/processed/stocktwits_sentiment_daily.csv")
FAILED_TICKERS_PATH = Path("data/processed/stocktwits_failed_tickers.csv")

# API / runtime parameters
DEFAULT_ZOOM = "ALL"
REQUEST_TIMEOUT = 60
MAX_RETRIES = 5
BACKOFF_BASE = 2.0
SLEEP_BETWEEN_SYMBOLS = 0.25
PROGRESS_LOG_EVERY = 25

# Aggregation method for daily sentiment-like variables
# "mean" is usually sensible for normalized scores
DAILY_AGGREGATIONS = {
    "messageVolume": "sum",
    "messageVolumeNormalized": "mean",
    "sentiment": "mean",
    "sentimentNormalized": "mean",
    "participationRatio": "mean",
    "participationRatioNormalized": "mean",
}


# =========================
# Logging
# =========================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


# =========================
# Helpers
# =========================

def format_seconds(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    return str(timedelta(seconds=seconds))


def ensure_directories() -> None:
    OUTPUT_RAW_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_DAILY_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    FAILED_TICKERS_PATH.parent.mkdir(parents=True, exist_ok=True)


def check_credentials() -> None:
    if not STOCKTWITS_USERNAME or not STOCKTWITS_PASSWORD:
        raise EnvironmentError(
            "Missing Stocktwits credentials. "
            "Please set STOCKTWITS_USERNAME and STOCKTWITS_PASSWORD as environment variables."
        )


def load_tickers(path: Path) -> list[str]:
    """
    Expects a CSV with either:
    - one column named 'ticker'
    - or one unnamed first column containing tickers
    """
    if not path.exists():
        raise FileNotFoundError(f"Ticker file not found: {path}")

    df = pd.read_csv(path)

    if "ticker" in df.columns:
        tickers = df["ticker"]
    else:
        tickers = df.iloc[:, 0]

    tickers = (
        tickers.astype(str)
        .str.upper()
        .str.strip()
        .replace({"": pd.NA, "NAN": pd.NA, "NONE": pd.NA})
        .dropna()
        .drop_duplicates()
        .tolist()
    )

    if not tickers:
        raise ValueError(f"No valid tickers found in {path}")

    return tickers


def get_with_retry(url: str, params: dict | None = None) -> dict:
    """
    Retry on temporary errors such as 429 / 5xx using exponential backoff.
    """
    auth = HTTPBasicAuth(STOCKTWITS_USERNAME, STOCKTWITS_PASSWORD)

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                url,
                params=params,
                auth=auth,
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                },
                timeout=REQUEST_TIMEOUT,
            )

            if response.status_code == 200:
                return response.json()

            if response.status_code in {429, 500, 502, 503, 504}:
                sleep_time = BACKOFF_BASE ** attempt
                logger.warning(
                    "Temporary API error %s for %s. Retry %s/%s in %.1f sec.",
                    response.status_code,
                    url,
                    attempt + 1,
                    MAX_RETRIES,
                    sleep_time,
                )
                time.sleep(sleep_time)
                continue

            response.raise_for_status()

        except requests.RequestException as exc:
            sleep_time = BACKOFF_BASE ** attempt
            logger.warning(
                "Request failed for %s. Retry %s/%s in %.1f sec. Error: %s",
                url,
                attempt + 1,
                MAX_RETRIES,
                sleep_time,
                exc,
            )
            time.sleep(sleep_time)

    raise RuntimeError(f"Request failed after {MAX_RETRIES} retries: {url}")


def fetch_symbol_chart(symbol: str, zoom: str = DEFAULT_ZOOM) -> dict:
    """
    Fetch chart data for one symbol from the Stocktwits sentiment API.
    """
    url = f"{BASE_URL}/{symbol}/chart"
    return get_with_retry(url, params={"zoom": zoom})


def chart_payload_to_df(symbol: str, payload: dict) -> pd.DataFrame:
    """
    Convert API JSON payload into a flat DataFrame.
    Expected structure:
    {
        "data": {
            "2026-03-15T10:00:00Z": {
                ...
            },
            ...
        }
    }
    """
    data = payload.get("data", {})

    if not isinstance(data, dict) or len(data) == 0:
        return pd.DataFrame()

    rows = []
    for dt_key, values in data.items():
        row = {
            "ticker": symbol,
            "dateTime": dt_key,
        }
        if isinstance(values, dict):
            row.update(values)
        rows.append(row)

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    df["dateTime"] = pd.to_datetime(df["dateTime"], utc=True, errors="coerce")
    df = df.dropna(subset=["dateTime"]).sort_values("dateTime").reset_index(drop=True)

    # Daily date for merge with CRSP-style panels
    df["date"] = df["dateTime"].dt.tz_convert("UTC").dt.floor("D").dt.tz_localize(None)

    return df


def fetch_many_symbols(symbols: Iterable[str], zoom: str = DEFAULT_ZOOM) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Returns:
    - raw combined dataframe
    - failed tickers dataframe
    """
    all_dfs: list[pd.DataFrame] = []
    failed_rows: list[dict] = []

    symbols = list(symbols)
    total = len(symbols)
    start_time = time.time()
    success_count = 0
    empty_count = 0
    failure_count = 0

    logger.info("Starting Stocktwits extraction for %s tickers.", total)

    for i, symbol in enumerate(symbols, start=1):
        symbol_start = time.time()
        logger.info("[%s/%s] Fetching %s", i, total, symbol)

        try:
            payload = fetch_symbol_chart(symbol, zoom=zoom)
            df_symbol = chart_payload_to_df(symbol, payload)

            if df_symbol.empty:
                empty_count += 1
                logger.warning("[%s/%s] No data returned for %s", i, total, symbol)
                failed_rows.append({"ticker": symbol, "reason": "empty_response"})
            else:
                success_count += 1
                all_dfs.append(df_symbol)
                logger.info(
                    "[%s/%s] Success for %s | rows=%s | elapsed=%s",
                    i,
                    total,
                    symbol,
                    len(df_symbol),
                    format_seconds(time.time() - symbol_start),
                )

        except Exception as exc:
            failure_count += 1
            logger.error("[%s/%s] Failed for %s: %s", i, total, symbol, exc)
            failed_rows.append({"ticker": symbol, "reason": str(exc)})

        elapsed_total = time.time() - start_time
        avg_per_symbol = elapsed_total / i
        remaining = total - i
        eta_seconds = avg_per_symbol * remaining

        if i % PROGRESS_LOG_EVERY == 0 or i == total:
            logger.info(
                "Progress: %s/%s (%.1f%%) | successes=%s | empty=%s | failed=%s | elapsed=%s | ETA=%s",
                i,
                total,
                100 * i / total,
                success_count,
                empty_count,
                failure_count,
                format_seconds(elapsed_total),
                format_seconds(eta_seconds),
            )

        time.sleep(SLEEP_BETWEEN_SYMBOLS)

    raw_df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
    failed_df = pd.DataFrame(failed_rows)

    logger.info(
        "Extraction finished | total=%s | successes=%s | empty=%s | failed=%s | elapsed=%s",
        total,
        success_count,
        empty_count,
        failure_count,
        format_seconds(time.time() - start_time),
    )

    return raw_df, failed_df


def aggregate_daily(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate intraday data to daily frequency.
    Only keeps aggregation columns that actually exist in the raw data.
    """
    if raw_df.empty:
        return pd.DataFrame()

    agg_dict = {col: func for col, func in DAILY_AGGREGATIONS.items() if col in raw_df.columns}

    if not agg_dict:
        raise ValueError("None of the expected aggregation columns were found in the raw Stocktwits data.")

    daily_df = (
        raw_df.groupby(["ticker", "date"], as_index=False)
        .agg(agg_dict)
        .sort_values(["ticker", "date"])
        .reset_index(drop=True)
    )

    return daily_df


def main() -> None:
    ensure_directories()
    check_credentials()

    tickers = load_tickers(INPUT_TICKERS_PATH)
    logger.info("Loaded %s tickers.", len(tickers))

    raw_df, failed_df = fetch_many_symbols(symbols=tickers, zoom=DEFAULT_ZOOM)

    if raw_df.empty:
        logger.warning("No raw data collected. Exiting.")
        if not failed_df.empty:
            failed_df.to_csv(FAILED_TICKERS_PATH, index=False)
            logger.info("Saved failed tickers to %s", FAILED_TICKERS_PATH)
        return

    # Save raw intraday/timestamp-level data
    raw_df.to_csv(OUTPUT_RAW_CSV_PATH, index=False)
    logger.info("Saved raw data to %s", OUTPUT_RAW_CSV_PATH)

    # Daily aggregation
    logger.info("Starting daily aggregation from %s raw rows.", len(raw_df))
    daily_df = aggregate_daily(raw_df)
    daily_df.to_csv(OUTPUT_DAILY_CSV_PATH, index=False)
    logger.info("Saved daily aggregated data to %s", OUTPUT_DAILY_CSV_PATH)

    # Failed tickers
    if not failed_df.empty:
        failed_df.to_csv(FAILED_TICKERS_PATH, index=False)
        logger.info("Saved failed tickers to %s", FAILED_TICKERS_PATH)

    logger.info("Done.")
    logger.info("Raw rows: %s", len(raw_df))
    logger.info("Daily rows: %s", len(daily_df))
    logger.info("Failed tickers: %s", len(failed_df))


if __name__ == "__main__":
    main()