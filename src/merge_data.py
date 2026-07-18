import pandas as pd
import matplotlib.pyplot as plt
from .data_loader import load_jgb_data, filter_window
from .fx_loader import load_usdjpy
from datetime import datetime

def build_merged_dataset(start_year=2011):
    jgb = load_jgb_data()
    jgb = filter_window(jgb, start_year=start_year)
    jgb = jgb.set_index('Date')

    fx = load_usdjpy(start=f"{start_year}-01-01")

    merged = jgb[['1Y', '10Y']].join(fx, how='inner')
    return merged

def add_slope(df):
    df = df.copy()
    df['slope_10y_1y'] = df['10Y'] - df['1Y']
    return df

def plot_slope(df):
    plt.figure(figsize=(12, 5))
    plt.plot(df.index, df['slope_10y_1y'])
    plt.axhline(0, color='red', linestyle='--', linewidth=1)
    plt.title('JGB 10Y-1Y Slope (2011-2026)')
    plt.ylabel('Slope (pp)')
    plt.savefig('notebooks/slope_plot.png')
    print("saved to notebooks/slope_plot.png")

def plot_raw_yields(df):
    plt.figure(figsize=(12, 5))
    plt.plot(df.index, df['1Y'], label='1Y yield')
    plt.plot(df.index, df['10Y'], label='10Y yield')
    plt.title('JGB 1Y vs 10Y Yield (2011-2026)')
    plt.ylabel('Yield (%)')
    plt.legend()
    plt.savefig('notebooks/raw_yields_plot.png')
    print("saved to notebooks/raw_yields_plot.png")
    
    
def add_volatility(df, window=30):
    df = df.copy()
    df['yield_change'] = df['10Y'].diff()
    df['vol_30d'] = df['yield_change'].rolling(window=window).std()
    return df

def plot_volatility(df):
    plt.figure(figsize=(12, 5))
    plt.plot(df.index, df['vol_30d'])
    plt.title('JGB 10Y Yield 30-Day Rolling Volatility (2011-2026)')
    plt.ylabel('Volatility (pp)')
    plt.savefig('notebooks/volatility_plot.png')
    print("saved to notebooks/volatility_plot.png")


def add_fx_change(df):
    df = df.copy()
    df['usdjpy_change'] = df['USDJPY'].pct_change() * 100
    return df


def compute_correlation(df, columns=('slope_10y_1y', 'vol_30d', 'usdjpy_change')):
    return df[list(columns)].corr()


def plot_correlation_heatmap(corr):
    plt.figure(figsize=(6, 5))
    plt.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
    plt.colorbar(label='Correlation')
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=45, ha='right')
    plt.yticks(range(len(corr.columns)), corr.columns)
    for i in range(len(corr.columns)):
        for j in range(len(corr.columns)):
            plt.text(j, i, f'{corr.iloc[i, j]:.2f}', ha='center', va='center')
    plt.title('Correlation: slope vs volatility vs USD/JPY daily change')
    plt.tight_layout()
    plt.savefig('notebooks/correlation_heatmap.png')
    print("saved to notebooks/correlation_heatmap.png")


def plot_scatter(df, x_col, y_col, title, filename):
    plt.figure(figsize=(6, 5))
    plt.scatter(df[x_col], df[y_col], s=10, alpha=0.5)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(f'notebooks/{filename}')
    print(f"saved to notebooks/{filename}")


if __name__ == "__main__":
    merged = build_merged_dataset()
    merged = add_slope(merged)
    merged = add_volatility(merged)
    merged = add_fx_change(merged)

    print(merged[['10Y', 'yield_change', 'vol_30d']].head(35))
    print(merged['vol_30d'].describe())

    plot_slope(merged)
    plot_raw_yields(merged)
    plot_volatility(merged)

    inverted = merged[merged['slope_10y_1y'] < 0]
    print(f"\nInverted on {len(inverted)} days")
    print(inverted[['1Y', '10Y', 'slope_10y_1y']])

    corr = compute_correlation(merged)
    print("\nCorrelation matrix (slope, vol_30d, usdjpy_change):")
    print(corr)
    plot_correlation_heatmap(corr)

    scatter_df = merged.dropna(subset=['slope_10y_1y', 'vol_30d', 'usdjpy_change'])
    plot_scatter(scatter_df, 'slope_10y_1y', 'vol_30d',
                 'Slope vs 30-day volatility', 'scatter_slope_vol.png')
    plot_scatter(scatter_df, 'slope_10y_1y', 'usdjpy_change',
                 'Slope vs USD/JPY daily change', 'scatter_slope_fx.png')