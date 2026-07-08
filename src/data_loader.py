import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "jgbcme_all.csv"


def load_jgb_data(path=DEFAULT_DATA_PATH):
    df = pd.read_csv(path, skiprows=1, na_values=['-'])
    df.columns = df.columns.str.strip()
    df['Date'] = pd.to_datetime(df['Date'], format='%Y/%m/%d')
    return df

def filter_window(df, start_year=2011):
    return df[df['Date'].dt.year >= start_year].reset_index(drop=True)

if __name__ == "__main__":
    df = load_jgb_data()
    print(df.dtypes)
    df_filtered = filter_window(df)
    print(df_filtered['Date'].min(), df_filtered['Date'].max())
    print(df_filtered[['Date', '1Y', '10Y']].isna().sum())
