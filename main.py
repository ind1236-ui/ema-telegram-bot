import ccxt
import pandas as pd
import requests
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

symbol = "BTC/USDT"
timeframe = "5m"
ema_periods = [9, 21, 50, 100, 200]

exchange = ccxt.binance()
last_signal = {}

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

print("EMA BOT STARTED")

while True:
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=200)
    df = pd.DataFrame(ohlcv, columns=['t','o','h','l','c','v'])

    for ema in ema_periods:
        df[f'EMA{ema}'] = df['c'].ewm(span=ema).mean()

    for i in range(len(ema_periods)-1):
        e1, e2 = ema_periods[i], ema_periods[i+1]
        prev, curr = df.iloc[-2], df.iloc[-1]

        key = f"{e1}_{e2}"

        if prev[f'EMA{e1}'] < prev[f'EMA{e2}'] and curr[f'EMA{e1}'] > curr[f'EMA{e2}']:
            if last_signal.get(key) != "UP":
                send_telegram(f"📈 EMA {e1} CROSS ABOVE {e2}")
                last_signal[key] = "UP"

        if prev[f'EMA{e1}'] > prev[f'EMA{e2}'] and curr[f'EMA{e1}'] < curr[f'EMA{e2}']:
            if last_signal.get(key) != "DOWN":
                send_telegram(f"📉 EMA {e1} CROSS BELOW {e2}")
                last_signal[key] = "DOWN"

    time.sleep(60)
