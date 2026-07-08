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