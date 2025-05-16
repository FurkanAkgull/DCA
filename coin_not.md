⚙️ Ekstra Gelişmişlik için:
24 saatlik ortalama düşüş %3 üzerindeyse, alım eşikleri daha esnek olabilir (örneğin %0.5 düşüşe de alım yapılabilir).

Ortalama düşüş yoksa ya da artış varsa, alımlar durdurulabilir.

Her alım ve satışta log kayıtları ve gerçek zamanlı Telegram bildirimleri ile izlenebilir.

api update : 

curl -X POST http://localhost:5001/update_config -H "Content-Type: application/json" -d "{\"symbol\":\"DOGEUSDT\", \"usdt_to_spend\":20, \"profit_target\":1.02, \"log_file\":\"orders_log.json\"}"
