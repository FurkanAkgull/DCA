import json
import time
from datetime import datetime
from binance.client import Client
import Dca_bot_check_coin
import Dca_bot_coin_histroy

API_KEY = Dca_bot_check_coin.API_KEY
API_SECRET = Dca_bot_check_coin.API_SECRET

client = Client(API_KEY, API_SECRET)

LOG_FILE = "bot.log"

def get_current_price(symbol):
    try:
        data = client.get_symbol_ticker(symbol=symbol)
        return float(data["price"])
    except Exception as e:
        print(f"[HATA] {symbol} fiyat alınamadı: {e}")
        return None

def load_thresholds():
    try:
        with open("coin_thresholds.json", "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[HATA] coin_thresholds.json okunamadı: {e}")
        return {}

def log_action(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

def execute_trade(symbol, quantity, action, buy_price=None):
    """
    Gerçek alım ve satım işlemleri yapacak fonksiyon.
    action: "buy" ya da "sell"
    """
    try:
        if action == "buy":
            # Burada alım işlemi yapılır
            order = client.order_market_buy(symbol=symbol, quantity=quantity)
            log_action(f"{symbol} için alım işlemi yapıldı: {order}")
            return float(order["fills"][0]["price"])  # Alım fiyatı döndürülür
        elif action == "sell":
            # Burada satış işlemi yapılır
            order = client.order_market_sell(symbol=symbol, quantity=quantity)
            log_action(f"{symbol} için satış işlemi yapıldı: {order}")
            sell_price = float(order["fills"][0]["price"])  # Satış fiyatı alınır

            # Kar/Zarar hesaplama
            profit = (sell_price - buy_price) * quantity
            log_action(f"{symbol} için satış sonrası kar/zarar: {profit:.6f} USDT")

    except Exception as e:
        log_action(f"[HATA] {symbol} işlemi yapılamadı: {e}")
        return None

def check_buy_opportunity():
    Dca_bot_coin_histroy.generate_thresholds()  # Bu fonksiyon history.py içinde olacak
    thresholds = load_thresholds()

    for symbol, data in thresholds.items():
        threshold_price = data["threshold_price"]
        current_price = get_current_price(symbol)

        if current_price is None:
            continue

        # Fiyat eşik altına düştüğünde alım yapılır ve loglanır
        if current_price < threshold_price:
            log_action(f"{symbol}: Fiyat {current_price:.6f} eşik {threshold_price:.6f} altında! (Simülasyon alım)")
            buy_price = execute_trade(symbol, 1, "buy")  # 1 miktarında alım işlemi gerçekleştir
            if buy_price:
                thresholds[symbol]["buy_price"] = buy_price  # Alım fiyatını kaydet
        # Fiyat eşik üstüne çıktığında satış yapılır ve loglanır
        elif current_price > threshold_price and "buy_price" in thresholds[symbol]:
            log_action(f"{symbol}: Fiyat {current_price:.6f} eşik {threshold_price:.6f} üstünde. Satış yapılacak!")
            execute_trade(symbol, 1, "sell", buy_price=thresholds[symbol]["buy_price"])  # Satış işlemi yapılır

def run_bot():
    while True:
        check_buy_opportunity()  # Alım fırsatlarını kontrol et
        time.sleep(300)  # 5 dakika (300 saniye) bekle

if __name__ == "__main__":
    run_bot()
