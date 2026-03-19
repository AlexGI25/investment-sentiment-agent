from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]

market_path = BASE_DIR / "src" / "market" / "market_data_with_indicators.csv"
macro_path = BASE_DIR / "src" / "macro" / "macro_data_monthly.csv"

market_data = pd.read_csv(market_path)
macro_data = pd.read_csv(macro_path)

market_data = market_data.sort_values(["Date", "Ticker"]).reset_index(drop=True)
macro_data = macro_data.sort_values("Date").reset_index(drop=True)

print("Market data:")
print(market_data.head())
print(market_data.shape)

print("\nMacro data before lag:")


print(macro_data.head(5))
macro_data[["CPI", "UNRATE", "FEDFUNDS"]] = macro_data[["CPI", "UNRATE", "FEDFUNDS"]].shift(1)

print("\nMacro after lag:")
print(macro_data.head(5))

# expand macro data from monthly to daily

# asigură-te din nou că Date este datetime normalizat
macro_data["Date"] = pd.to_datetime(macro_data["Date"]).dt.normalize()

# păstrează doar coloanele de interes
macro_data = macro_data[["Date", "CPI", "UNRATE", "FEDFUNDS"]].copy()

# pune Date ca index
macro_data = macro_data.set_index("Date").sort_index()

# creează index zilnic
daily_index = pd.date_range(start="2018-01-01", end="2025-12-31", freq="D")

# reindex + forward fill
macro_daily = macro_data.reindex(daily_index).ffill()

# aduce indexul înapoi în coloană
macro_daily = macro_daily.reset_index().rename(columns={"index": "Date"})

print("\nMacro daily:")
print(macro_daily.head(10))
print(macro_daily.tail(10))
print(macro_daily.shape)
print(macro_daily.isna().sum())

# merge market data with micro daily

market_data["Date"] = pd.to_datetime(market_data["Date"]).dt.normalize()
macro_daily["Date"] = pd.to_datetime(macro_daily["Date"]).dt.normalize()

final_data = market_data.merge(macro_daily, on="Date", how="left")

print("\nFinal merged data:")
print(final_data.head())
print(final_data.shape)

print("\nNaN after merge:")
print(final_data[["CPI", "UNRATE", "FEDFUNDS"]].isna().sum())

final_data = final_data.sort_values(["Ticker", "Date"]).reset_index(drop=True)

final_data.to_csv("market_macro_data.csv", index=False, date_format="%Y-%m-%d")