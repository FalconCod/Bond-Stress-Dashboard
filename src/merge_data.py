import pandas as pd
from .data_loader import load_jgb_data, filter_window
from .fx_loader import load_usdjpy

def build_merged_dataset(start_year=2011):
    jgb = load_jgb_data()
    jgb = filter_window(jgb, start_year=start_year)
    jgb = jgb.set_index('Date')

    fx = load_usdjpy(start=f"{start_year}-01-01")

    merged = jgb[['1Y', '10Y']].join(fx, how='inner')
    return merged

if __name__ == "__main__":
    merged = build_merged_dataset()
    print(merged.head())
    print(merged.tail())
    print(merged.shape)
    print(merged.isna().sum())