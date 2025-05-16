import json
import time
from datetime import datetime
import simulator_check
import threading

#Statick
anapara = 100.0

# Arka planda fiyat verisini çeksin
threading.Thread(target=simulator_check.main, daemon=True).start()
SYMBOL = "DOGEUSDT"
# === LOG DOSYASI ===
LOG_FILE = "dca_log.json"
def log_message(message, log_file="log_messages.json"):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "message": message
    }
    try:
        with open(log_file, "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append(entry)
    with open(log_file, "w") as f:
        json.dump(data, f, indent=2)

# === Ortalama Fiyat Hesapla ===
def average_price():
    price_list = simulator_check.price_list
    if not price_list:
        return 0.0
    return round(sum(price_list) / len(price_list), 6)

# === ALIM ===
def simulate_buy(symbol, _price, amount_usdt, log_file):
    global anapara
    quantity = amount_usdt / _price
    avg_price = average_price()
    buy_price = round(avg_price * 0.99, 6)

    anapara -= amount_usdt  # Anaparayı güncelle

    order = {
        "timestamp": datetime.utcnow().isoformat(),
        "symbol": symbol,
        "_price": _price,
        "quantity": quantity,
        "side": "BUY",
        "average_price": avg_price,
        "buy_price": buy_price,
        "anapara": round(anapara, 2)
    }

    print(f"[ALIM] {symbol}: {quantity:.4f} adet @ {_price:.4f} USDT")
    print(f"Ortalama Fiyat: {avg_price:.4f} → %1 Düşük Fiyat: {buy_price:.4f} USDT")
    print(f"Yeni Anapara: {anapara:.2f} USDT")
    log_order(order, log_file)
    return quantity

# === SATIM ===
def simulate_sell(symbol, _price, quantity, log_file):
    global anapara
    avg_price = average_price()
    sell_price = round(avg_price * 1.01, 6)

    gelir = quantity * _price
    anapara += gelir  # Anaparayı güncelle

    order = {
        "timestamp": datetime.utcnow().isoformat(),
        "symbol": symbol,
        "_price": _price,
        "quantity": quantity,
        "side": "SELL",
        "average_price": avg_price,
        "sell_price": sell_price,
        "anapara": round(anapara, 2)
    }

    print(f"[SATIM] {symbol}: {quantity:.4f} adet @ {_price:.4f} USDT")
    print(f"Ortalama Fiyat: {avg_price:.4f} → %1 Yüksek Fiyat: {sell_price:.4f} USDT")
    print(f"Yeni Anapara: {anapara:.2f} USDT")
    log_order(order, log_file)
    return gelir

# === LOG KAYDI ===
def log_order(order, log_file):
    try:
        with open(log_file, "r") as f:
            data = json.load(f)
    except:
        data = []
    data.append(order)
    with open(log_file, "w") as f:
        json.dump(data, f, indent=2)

# === VARLIKLARI HESAPLA ===
def get_holdings(symbol, log_file):
    try:
        with open(log_file, "r") as f:
            orders = json.load(f)
    except:
        return 0

    total = 0
    for o in orders:
        if o["symbol"] != symbol:
            continue
        if o["side"] == "BUY":
            total += o["quantity"]
        elif o["side"] == "SELL":
            total -= o["quantity"]
    return total

# === ANA BOT ===
def run_dca_bot():
    log_file = "dca_orders.json"
    message_log_file = "dca_log.json"

    while True:
        if not simulator_check.price_list:
            msg = "Fiyat alınamadı. Tekrar deneniyor..."
            print(msg)
            log_message(msg, message_log_file)
            time.sleep(3)
            continue

        current_price = simulator_check.price_list[-1]
        avg_price = average_price()

        print(f"\nGüncel Fiyat: {current_price:.6f}")
        print(f"Ortalama Fiyat: {avg_price:.6f}")

        log_message(f"Güncel Fiyat: {current_price}", message_log_file)
        log_message(f"Ortalama Fiyat: {avg_price}", message_log_file)

        holdings = get_holdings(SYMBOL, log_file)

        buy_threshold = avg_price * 0.99  # Ortalama fiyatın %1 altı
        sell_threshold = avg_price * 1.01  # Ortalama fiyatın %1 üstü

        if holdings > 0 and current_price >= sell_threshold:
            msg = f"{SYMBOL} bakiyesi: {holdings:.4f} — Satış yapılacak."
            print(msg)
            log_message(msg, message_log_file)
            simulate_sell(SYMBOL, current_price, holdings, log_file)

        elif holdings == 0 and current_price <= buy_threshold:
            msg = f"{SYMBOL} bakiyesi yok — Alım yapılacak."
            print(msg)
            log_message(msg, message_log_file)
            simulate_buy(SYMBOL, current_price, 10, log_file)  # 10 USDT ile alım

        else:
            msg = f"Alım veya satım koşulları sağlanmadı. Bekleniyor..."
            print(msg)
            log_message(msg, message_log_file)

        time.sleep(3)
# === ÇALIŞTIR ===
if __name__ == "__main__":
    run_dca_bot()
