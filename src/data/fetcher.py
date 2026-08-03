"""
fetcher.py - Market data loader using yfinance with intelligent offline/mock fallback and robust column flattening.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.core.config import DEFAULT_KLSE_STOCKS

def _safe_float(val, default=0.0):
    try:
        if val is None or (isinstance(val, str) and val.strip().upper() in ('N/A', 'NONE', 'NAN', '')):
            return float(default)
        v = float(val)
        return float(default) if np.isnan(v) or np.isinf(v) else v
    except (ValueError, TypeError):
        return float(default)

def fetch_klse_stock_data(symbol: str, period: str = "2y"):
    """
    Fetches price history and fundamentals for a given KLSE ticker (e.g. '1155.KL').
    Flattens multi-index columns from yfinance and falls back to synthetic data if offline.
    """
    symbol_formatted = symbol.strip().upper()
    if not symbol_formatted.endswith(".KL") and symbol_formatted.isdigit():
        symbol_formatted += ".KL"

    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol_formatted)
        df = ticker.history(period=period)
        info = ticker.info if hasattr(ticker, "info") else {}
        
        if df.empty or len(df) < 50:
            return _generate_mock_data(symbol_formatted, days=500)

        # Flatten multi-level columns if returned by yfinance
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Ensure single series column names
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        for col in required_cols:
            if col not in df.columns:
                return _generate_mock_data(symbol_formatted, days=500)
            if isinstance(df[col], pd.DataFrame):
                df[col] = df[col].iloc[:, 0]

        curr_p = _safe_float(info.get("currentPrice") or info.get("regularMarketPrice") or df['Close'].iloc[-1], default=df['Close'].iloc[-1])
        high_52 = _safe_float(info.get("fiftyTwoWeekHigh"), default=df['Close'].max())
        low_52 = _safe_float(info.get("fiftyTwoWeekLow"), default=df['Close'].min())

        fundamentals = {
            "name": str(info.get("shortName") or info.get("longName") or DEFAULT_KLSE_STOCKS.get(symbol_formatted, {}).get("name", symbol_formatted)),
            "sector": str(info.get("sector") or DEFAULT_KLSE_STOCKS.get(symbol_formatted, {}).get("sector", "General")),
            "pe_ratio": _safe_float(info.get("trailingPE") or info.get("forwardPE"), default=14.5),
            "pb_ratio": _safe_float(info.get("priceToBook"), default=1.2),
            "roe": _safe_float(info.get("returnOnEquity"), default=0.10) * 100 if isinstance(info.get("returnOnEquity"), (int, float)) else 10.0,
            "debt_to_equity": _safe_float(info.get("debtToEquity"), default=45.0),
            "dividend_yield": _safe_float(info.get("dividendYield"), default=0.035) * 100 if isinstance(info.get("dividendYield"), (int, float)) else 3.5,
            "market_cap": int(_safe_float(info.get("marketCap"), default=5_000_000_000)),
            "fifty_two_week_high": round(high_52, 2),
            "fifty_two_week_low": round(low_52, 2),
            "current_price": round(curr_p, 2)
        }
        
        return df, fundamentals

    except Exception as e:
        return _generate_mock_data(symbol_formatted, days=500)

def _generate_mock_data(symbol: str, days: int = 500):
    """Generates synthetic daily trading history for offline/demo operation."""
    np.random.seed(abs(hash(symbol)) % 100000)
    end_date = datetime.now()
    dates = [end_date - timedelta(days=i*1.4) for i in range(days)]
    dates.reverse()

    base_price = np.random.uniform(1.5, 12.0)
    returns = np.random.normal(0.0006, 0.016, size=days)
    price_series = base_price * np.exp(np.cumsum(returns))

    high = price_series * (1 + np.abs(np.random.normal(0, 0.009, size=days)))
    low = price_series * (1 - np.abs(np.random.normal(0, 0.009, size=days)))
    open_p = low + (high - low) * np.random.uniform(0.2, 0.8, size=days)
    volume = np.random.randint(100_000, 5_000_000, size=days)

    df = pd.DataFrame({
        "Open": open_p,
        "High": high,
        "Low": low,
        "Close": price_series,
        "Volume": volume
    }, index=pd.DatetimeIndex(dates))

    stock_meta = DEFAULT_KLSE_STOCKS.get(symbol, {"name": f"KLSE Listed Co ({symbol})", "sector": "Industrial & Services"})

    fundamentals = {
        "name": stock_meta["name"],
        "sector": stock_meta["sector"],
        "pe_ratio": round(np.random.uniform(8.0, 22.0), 2),
        "pb_ratio": round(np.random.uniform(0.8, 2.5), 2),
        "roe": round(np.random.uniform(8.0, 18.0), 2),
        "debt_to_equity": round(np.random.uniform(20.0, 80.0), 2),
        "dividend_yield": round(np.random.uniform(2.5, 6.0), 2),
        "market_cap": int(np.random.uniform(500_000_000, 20_000_000_000)),
        "fifty_two_week_high": round(float(df['Close'].iloc[-250:].max()), 2),
        "fifty_two_week_low": round(float(df['Close'].iloc[-250:].min()), 2),
        "current_price": round(float(df['Close'].iloc[-1]), 2)
    }

    return df, fundamentals
