import logging
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

API_KEY = '423Fb02F70d0F65af4840F24CC3C9d6ez5igM7Kz5A3CBbBALOr3qbpVpLjpwel3'
API_SECRET = 'AB3488BFe4660FdA37d4F802C69Bb013zwJfDSvteMTUISHdxmI8BchtOX8K7SHZ'

client = Client(API_KEY, API_SECRET, {"timeout": 10})

class DcaCoin:
    def __init__(self, symbol):
        self.symbol = symbol
        self.client = client
        self.last_price = None
        self.price = None

    def get_price(self, retries=3, delay=2):
        for attempt in range(retries):
            try:
                data = self.client.get_symbol_ticker(symbol=self.symbol)
                return float(data['price'])
            except BinanceAPIException as e:
                logging.warning(f"[{self.symbol}] Binance API hatası (attempt {attempt+1}): {e}")
            except BinanceRequestException as e:
                logging.warning(f"[{self.symbol}] Binance isteği başarısız (attempt {attempt+1}): {e}")
            except Exception as e:
                logging.warning(f"[{self.symbol}] Genel hata (attempt {attempt+1}): {e}")
            
            time.sleep(delay)  # Bekle ve yeniden dene
        
        logging.error(f"[GENEL HATA] {self.symbol}: Tüm bağlantı denemeleri başarısız oldu.")
        return None

    def should_buy(self):
        self.price = self.get_price()
        if self.price is None:
            return False

        if self.last_price is None:
            self.last_price = self.price
            return False

        if self.price < self.last_price * 0.99:
            logging.info(f"{self.symbol}: %1'den fazla düşüş tespit edildi.")
            self.last_price = self.price
            return True
        else:
            logging.info(f"{self.symbol}: Düşüş eşiği geçilmedi.")
            self.last_price = self.price
            return False
