from pathlib import Path

import pandas as pd
import yfinance as yf

CACHE_PATH = Path(__file__).resolve().parents[1] / "data" / "cache" / "usdjpy.csv"


def _fetch_live(start, end):
    data = yf.download("JPY=X", start=start, end=end)
    data = pd.DataFrame(data)
    if data.empty:
        return None
    data.columns = data.columns.get_level_values(0)
    return data[["Close"]].rename(columns={"Close": "USDJPY"})


def load_usdjpy(start="2011-01-01", end=None):
    """Pulls USD/JPY from yfinance, with a disk cache fallback.

    yfinance rate-limits aggressively (YFRateLimitError) under repeated
    calls — common during local dev when the app restarts often. Rather
    than crash the whole page on a transient failure, fall back to the
    last successfully fetched copy on disk and keep the cache fresh
    whenever a live pull does succeed.
    """
    fx = _fetch_live(start, end)

    if fx is not None:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        fx.to_csv(CACHE_PATH)
        return fx

    if CACHE_PATH.exists():
        cached = pd.read_csv(CACHE_PATH, index_col=0, parse_dates=True)
        return cached

    raise RuntimeError(
        "USD/JPY fetch from yfinance failed (likely rate-limited) and no "
        f"cached copy exists yet at {CACHE_PATH}. Wait a few minutes and "
        "retry, or run this once when not rate-limited to seed the cache."
    )


if __name__ == "__main__":
    fx = load_usdjpy()
    print(fx.head())
    print(fx.tail())
    print(fx.isna().sum())
    print(fx.columns)
