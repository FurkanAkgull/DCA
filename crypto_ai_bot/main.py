import os
import sys
import time
import json
import requests
import logging
import datetime
from configparser import ConfigParser
import pandas as pd

from binance_api.fetcher import get_historical_data, save_data
from ai.predictor import make_prediction
from strategy.signal_generator import generate_signal

# === Settings ===
SYMBOL = "DOGEUSDT"
LOG_DIR = "logs"
LOG_ORDER_FILE = os.path.join(LOG_DIR, "dca_orders.json")
LOG_MSG_FILE = os.path.join(LOG_DIR, "dca_log.json")
capital = 100  # Test COIN

# === Create Files & Logs ===
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "run.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def log_message(msg, file):
    try:
        with open(file, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.utcnow().isoformat()} - {msg}\n")
    except Exception as e:
        print(f"[LOG ERROR] {e}")

# === Market Analysis ===

def check_analysis():
    prices = fetch_price_list(interval="1m", limit=1440)  # 24 Hours = 1440 Minutes

    if not prices:
        log_message("check_analysis: Could not fetch price data.", LOG_MSG_FILE)
        return

    start_price = prices[0]
    end_price = prices[-1]
    min_price = min(prices)
    max_price = max(prices)
    change_percent = ((end_price - start_price) / start_price) * 100
    volatility = (max_price - min_price) / start_price * 100

    if change_percent > 1:
        trend = "Uptrend"
    elif change_percent < -1:
        trend = "Downtrend"
    else:
        trend = "Stable"

    analysis = {
        "Start Price": round(start_price, 6),
        "End Price": round(end_price, 6),
        "Min Price": round(min_price, 6),
        "Max Price": round(max_price, 6),
        "Change (%)": round(change_percent, 2),
        "Volatility (%)": round(volatility, 2),
        "Trend": trend
    }

    print("\n📊 24-Hour Price Analysis:")
    for k, v in analysis.items():
        print(f"{k}: {v}")

    log_message(f"check_analysis Response: {json.dumps(analysis, ensure_ascii=False)}", LOG_MSG_FILE)
    return analysis

# === Fetch prices from Binance API ===
def fetch_price_list(symbol=SYMBOL, interval="1m", limit=50):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return [float(kline[4]) for kline in data]  # Closing prices
    except Exception as e:
        log_message(f"[Error] Binance API: {e}", LOG_MSG_FILE)
        return []

def average_price(symbol=SYMBOL):
    prices = fetch_price_list(symbol)
    return round(sum(prices) / len(prices), 6) if prices else 0.0

# === BUY ===
def buy(symbol, price, usdt_amount, log_file):
    global capital
    quantity = usdt_amount / price
    avg = average_price(symbol)
    buy_price = round(avg * 0.99, 6)
    capital -= usdt_amount

    order = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "symbol": symbol,
        "side": "BUY",
        "price": price,
        "quantity": quantity,
        "average_price": avg,
        "buy_price": buy_price,
        "capital": round(capital, 2)
    }
    log_order(order, log_file)
    print(f"[BUY] {symbol}: {quantity:.4f} units bought @ {price:.4f}")
    return quantity

# === SELL ===
def sell(symbol, price, quantity, log_file):
    global capital
    avg = average_price(symbol)
    sell_price = round(avg * 1.01, 6)
    income = price * quantity
    capital += income

    order = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "symbol": symbol,
        "side": "SELL",
        "price": price,
        "quantity": quantity,
        "average_price": avg,
        "sell_price": sell_price,
        "capital": round(capital, 2)
    }
    log_order(order, log_file)
    print(f"[SELL] {symbol}: {quantity:.4f} units sold @ {price:.4f}")
    return income

def log_order(order, file):
    try:
        if os.path.exists(file):
            with open(file, "r") as f:
                data = json.load(f)
        else:
            data = []
        data.append(order)
        with open(file, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log_message(f"[LOG ORDER ERROR] {e}", LOG_MSG_FILE)

def get_holdings(symbol, file):
    try:
        with open(file, "r") as f:
            orders = json.load(f)
    except:
        return 0
    total = 0
    for o in orders:
        if o["symbol"] != symbol:
            continue
        total += o["quantity"] if o["side"] == "BUY" else -o["quantity"]
    return total

# === AI SIGNAL ===
def run_ai_signal():
    df = get_historical_data(SYMBOL, "1h", 100)
    save_data(df)
    prediction = make_prediction(df)
    signal = generate_signal(prediction)
    print(f"[AI SIGNAL] {signal}")
    return signal

# === MAIN DCA FUNCTION ===
def run_dca_function():
    global capital
    while True:
        signal = run_ai_signal()
        analysis = check_analysis()

        if not analysis:
            log_message("Analysis failed, retrying...", LOG_MSG_FILE)
            time.sleep(60)
            continue

        if signal == "hold":
            log_message("Market stable. DCA is on hold.", LOG_MSG_FILE)
            print("[AI] HOLD signal, no action taken...")
            time.sleep(300)
            continue

        if analysis["Trend"] == "Downtrend":
            log_message("Trend is down. No action taken.", LOG_MSG_FILE)
            time.sleep(300)
            continue

        if analysis["Volatility (%)"] < 3:
            log_message("Volatility is low. No action taken.", LOG_MSG_FILE)
            time.sleep(300)
            continue

        prices = fetch_price_list()
        if not prices:
            log_message("Price data unavailable.", LOG_MSG_FILE)
            time.sleep(5)
            continue

        current_price = prices[-1]
        avg = average_price()
        holdings = get_holdings(SYMBOL, LOG_ORDER_FILE)

        print(f"\nPrice: {current_price:.6f} | Average: {avg:.6f}")
        buy_threshold = avg * 0.99
        sell_threshold = avg * 1.01

        if holdings > 0 and current_price >= sell_threshold and signal == "sell":
            sell(SYMBOL, current_price, holdings, LOG_ORDER_FILE)
            log_message("SELL executed.", LOG_MSG_FILE)

        elif holdings == 0 and current_price <= buy_threshold and signal == "buy":
            buy(SYMBOL, current_price, 10, LOG_ORDER_FILE)
            log_message("BUY executed.", LOG_MSG_FILE)

        else:
            log_message("Trade conditions not met.", LOG_MSG_FILE)

        time.sleep(60)

# === RUN ===
if __name__ == "__main__":
    run_dca_function()
