# Crypto AI Bot

This project is an AI-powered trading signal generator for cryptocurrency markets using Binance API and technical indicators.

## 📌 Features

- Fetches live price data from Binance
- Adds technical indicators (RSI, EMA, MACD)
- Trains a machine learning model (Random Forest Classifier) on historical data
- Predicts if the next candle will be bullish or bearish
- Generates buy/sell signals based on predictions
- Can be extended to automatically execute trades

---

## 🧠 AI Model

The AI model uses the following features to make predictions:

- RSI (Relative Strength Index)
- EMA (Exponential Moving Average)
- MACD (Moving Average Convergence Divergence)

It is trained to predict whether the next closing price will be higher than the current one.

crypto_ai_bot/
├── ai/                    # Model training and prediction
├── analysis/              # Technical indicators and feature engineering
├── binance_api/           # Binance API integration
├── data/                  # Historical CSV data
├── models/                # Saved AI models
├── strategy/              # Signal generation and trade execution
├── main.py                # Main execution file
├── requirements.txt       # Python dependencies
└── config.yaml            # Configuration and API keys

---

## ⚙️ Requirements

Install required packages:

```bash
pip install -r requirements.txt
python ai/trainer.py
models/rfc_model.pkl
python main.py
