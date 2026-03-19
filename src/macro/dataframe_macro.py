import pandas as pd
from pandas_datareader import data as web

start_date = "2017-12-01"
end_date = "2025-12-31"

fred_series = {
    "CPI": "CPIAUCSL",
    "UNRATE": "UNRATE",
    "FEDFUNDS": "FEDFUNDS"
}

macro_data = pd.DataFrame()

for column_name, fred_code in fred_series.items():
    macro_data[column_name] = web.DataReader(
        fred_code,
        "fred",
        start_date,
        end_date
    )

print(macro_data.head())
print(macro_data.tail())
print(macro_data.info())

macro_data = macro_data.reset_index()

macro_data = macro_data.rename(columns={"DATE": "Date"})

macro_data = macro_data[["Date", "CPI", "UNRATE", "FEDFUNDS"]]

macro_data["Date"] = pd.to_datetime(macro_data["Date"])

macro_data = macro_data.sort_values("Date").drop_duplicates().reset_index(drop=True)

print(macro_data.head())
print(macro_data.tail())
print(macro_data.info())

macro_data[["CPI", "UNRATE", "FEDFUNDS"]] = macro_data[["CPI", "UNRATE", "FEDFUNDS"]].ffill()

print(macro_data.isna().sum())
print(macro_data.head())
print(macro_data.tail())
print(macro_data.info())

macro_data.to_csv("macro_data_monthly.csv", index=False)