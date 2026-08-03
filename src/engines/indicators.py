"""
indicators.py - Technical indicator calculation utilities.
"""

import pandas as pd
import numpy as np

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculates EMA 20/50/200, RSI 14, ATR 14, MACD, and 20-day High/Low bounds."""
    df = df.copy()
    close = df['Close']
    high = df['High']
    low = df['Low']

    # EMAs
    df['EMA_20'] = close.ewm(span=20, adjust=False).mean()
    df['EMA_50'] = close.ewm(span=50, adjust=False).mean()
    df['EMA_200'] = close.ewm(span=200, adjust=False).mean()

    # RSI (14)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=14, min_periods=14).mean()
    avg_loss = loss.rolling(window=14, min_periods=14).mean()
    rs = avg_gain / (avg_loss + 1e-9)
    df['RSI_14'] = 100 - (100 / (1 + rs))

    # ATR (14)
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df['ATR_14'] = tr.rolling(window=14, min_periods=1).mean()

    # MACD (12, 26, 9)
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    df['MACD_Line'] = ema_12 - ema_26
    df['MACD_Signal'] = df['MACD_Line'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD_Line'] - df['MACD_Signal']

    # 20-day High & Low
    df['High_20'] = high.rolling(window=20).max()
    df['Low_20'] = low.rolling(window=20).min()

    return df
