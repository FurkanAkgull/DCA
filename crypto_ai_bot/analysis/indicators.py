import pandas as pd
import pandas_ta as ta

def add_indicators(df):
    df['rsi'] = ta.rsi(df['close'], length=14)
    df['ema'] = ta.ema(df['close'], length=14)
    df['macd'] = ta.macd(df['close'])['MACD_12_26_9']
    df.dropna(inplace=True)
    return df
