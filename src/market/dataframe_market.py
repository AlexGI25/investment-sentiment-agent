import yfinance as yf
import pandas as pd

tickers = ["AAPL", "MSFT", "NVDA", "META", "TSLA", "AMZN", "JPM", "XOM", "UNH", "AMD"]

start_date = "2018-01-01"
end_date = "2026-01-01"

data = yf.download(
    tickers=tickers,
    start=start_date,
    end=end_date,
    interval="1d",
    group_by="ticker",
    auto_adjust=False
)

print(data.head())

# turn date index into column
data = data.stack(level=0).reset_index()

data = data.rename(columns={
    "level_1": "Ticker"
})

data = data[["Date", "Ticker", "Open", "High", "Low", "Close", "Adj Close", "Volume"]]

data = data.sort_values(by=["Date", "Ticker"]).reset_index(drop=True)
data.columns.name = None
print(data.head(15))
print(data.shape)

print(data.isna().sum())

############ tecnical indicators

#1  ret_1d
data = data.sort_values(["Ticker", "Date"])

data["ret_1d"] = data.groupby("Ticker")["Close"].pct_change()

print(data[["Date", "Ticker", "Close", "ret_1d"]].head(15))

#2 ret_5d

data["ret_5d"] = data.groupby("Ticker")["Close"].pct_change(periods=5)

print(data[["Date", "Ticker", "Close", "ret_1d", "ret_5d"]].head(12))

#3 vol_10d

data["vol_10d"] = (
    data.groupby("Ticker")["ret_1d"]
    .rolling(window=10)
    .std()
    .reset_index(level=0, drop=True)
)

print(data[["Date", "Ticker", "ret_1d", "vol_10d"]].head(20))

#4 sma_10

data["sma_10"] = (
    data.groupby("Ticker")["Close"]
    .rolling(window=10)
    .mean()
    .reset_index(level=0, drop=True)
)

#5 sma_20

data["sma_20"] = (
    data.groupby("Ticker")["Close"]
    .rolling(window=20)
    .mean()
    .reset_index(level=0, drop=True)
)

print(data[["Date", "Ticker", "Close", "sma_10", "sma_20"]].head(25))

#6 ema_10

data["ema_10"] = data.groupby("Ticker")["Close"].transform(
    lambda x: x.ewm(span=10, adjust=False).mean()
)

print(data[["Date", "Ticker", "Close", "sma_10", "ema_10"]].head(20))

#7 rsi_14

def compute_rsi(series, window=14):
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))
    return rsi


data["rsi_14"] = data.groupby("Ticker")["Close"].transform(
    lambda x: compute_rsi(x, 14)
)

print(data[["Date", "Ticker", "Close", "rsi_14"]].head(25))

#8,9 macd, macd signal

data["ema_12"] = data.groupby("Ticker")["Close"].transform(
    lambda x: x.ewm(span=12, adjust=False).mean()
)

data["ema_26"] = data.groupby("Ticker")["Close"].transform(
    lambda x: x.ewm(span=26, adjust=False).mean()
)

data["macd"] = data["ema_12"] - data["ema_26"]

data["macd_signal"] = data.groupby("Ticker")["macd"].transform(
    lambda x: x.ewm(span=9, adjust=False).mean()
)

print(data[["Date", "Ticker", "Close", "macd", "macd_signal"]].head(30))

data_final = data.dropna().copy()
data_final = data_final.drop(columns=["ema_12", "ema_26"])

print(data.shape)
print(data_final.shape)
print(data_final.isna().sum())
print(data_final.head())

data_final.to_csv("market_data_with_indicators.csv", index=False)