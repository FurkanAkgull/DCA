import json
from binance.client import Client
import logging
import time
import Dca_bot_check_coin

API_KEY = Dca_bot_check_coin.API_KEY
API_SECRET = Dca_bot_check_coin.API_SECRET

client = Client(API_KEY, API_SECRET, {"timeout": 10})

COINS = ["DOGEUSDT", "LINKUSDT", "SOLUSDT", "XRPUSDT", "SHIBUSDT", "ADAUSDT"]

def get_24h_change(symbol):
    try:
        ticker = client.get_ticker(symbol=symbol)
        price = float(ticker["lastPrice"])
        change_percent = float(ticker["priceChangePercent"])
        return price, change_percent
    except Exception as e:
        logging.warning(f"{symbol} için veri alınamadı: {e}")
        return None, None

def generate_thresholds():
    thresholds = {}
    for coin in COINS:
        price, change = get_24h_change(coin)
        if price is not None and change is not None:
            # %1 düşüş eşiği: fiyat * 0.99
            threshold = price * 0.99
            thresholds[coin] = {
                "current_price": price,
                "threshold_price": round(threshold, 6),
                "24h_change": change
            }
        time.sleep(1)

    with open("coin_thresholds.json", "w") as f:
        json.dump(thresholds, f, indent=4)
    print("Eşikler başarıyla kaydedildi.")

if __name__ == "__main__":
    generate_thresholds()
