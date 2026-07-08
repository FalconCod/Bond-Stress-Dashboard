# import yfinance as yf

# def load_usdjpy(start="2011-01-01", end=None):
#     try:
#         data = yf.download("JPY=X", start=start, end=end, progress=False, auto_adjust=False)
#     except Exception as exc:
#         raise RuntimeError(f"Failed to download USD/JPY data: {exc}") from exc

#     if data is None or data.empty:
#         raise ValueError("No USD/JPY data returned by yfinance.")

#     if "Close" not in data.columns:
#         raise KeyError(f"Expected 'Close' column, got: {list(data.columns)}")

#     return data[["Close"]].rename(columns={"Close": "USDJPY"})

# if __name__ == "__main__":
#     fx = load_usdjpy()
#     print(fx.head())
#     print(fx.tail())
#     print(fx.isna().sum())


import yfinance as yf
import pandas as pd

def load_usdjpy(start="2011-01-01", end=None):
    data = yf.download("JPY=X", start=start, end=end)
    data = pd.DataFrame(data)  # explicit cast, satisfies type checker
    data.columns = data.columns.get_level_values(0)
    return data[['Close']].rename(columns={'Close': 'USDJPY'})

if __name__ == "__main__":
    fx = load_usdjpy()
    print(fx.head())
    print(fx.tail())
    print(fx.isna().sum())
    print(fx.columns)