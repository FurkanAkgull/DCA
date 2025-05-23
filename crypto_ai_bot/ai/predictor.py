import joblib
import pandas as pd
from analysis.indicators import add_indicators

def load_model():
    return joblib.load('models/rfc_model.pkl')

def make_prediction(df):
    df = add_indicators(df)
    model = load_model()
    X = df[['rsi', 'ema', 'macd']]
    return model.predict(X)[-1]
