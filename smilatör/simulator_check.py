import requests
import time

API_URL = "http://127.0.0.1:5001/get_config"  
price_list = [] 
def average_price():
    if price_list:
        avg = sum(price_list) / len(price_list)
        return round(avg, 4)
    return 0.0
def fetch_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        price = data.get("price")
        symbol = data.get("symbol")
        if price is not None:
            price_list.append(price)

        print(f"Gelen Veri: {symbol} = {price}  Ortalama Veri: {average_price()}")
        
    except requests.RequestException as e:
        print("API Hatası:", e)
        
def main():
    while True:
        fetch_data()
        time.sleep(3)

if __name__ == "__main__":
    main()
