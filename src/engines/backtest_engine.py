"""
backtest_engine.py - Historical Walk-Forward Simulation Engine for KLSE Stocks.
Simulates historical trades over 1-year window to quantify strategy performance.
"""

import pandas as pd
import numpy as np
from src.data.fetcher import fetch_klse_stock_data
from src.engines.indicators import calculate_technical_indicators
from src.core.config import DEFAULT_KLSE_STOCKS

def backtest_single_stock(ticker: str, initial_capital: float = 10000.0) -> dict:
    """Runs historical walk-forward backtest for a single stock."""
    df, fun = fetch_klse_stock_data(ticker, period="2y")
    if df.empty or len(df) < 150:
        return {"ticker": ticker, "trades": [], "total_return_pct": 0.0, "win_rate": 0.0}

    df_calc = calculate_technical_indicators(df)
    
    # Restrict to past 250 trading days (~1 year)
    test_df = df_calc.iloc[-250:]

    in_position = False
    entry_price = 0.0
    target_price = 0.0
    stop_loss = 0.0
    entry_date = None

    trades = []
    
    for i in range(len(test_df)):
        row = test_df.iloc[i]
        date_str = test_df.index[i].strftime("%Y-%m-%d") if hasattr(test_df.index[i], "strftime") else str(test_df.index[i])
        close_p = float(row['Close'])
        high_p = float(row['High'])
        low_p = float(row['Low'])
        ema_200 = float(row['EMA_200'])
        rsi = float(row['RSI_14']) if not np.isnan(row['RSI_14']) else 50.0
        atr = float(row['ATR_14']) if not np.isnan(row['ATR_14']) else close_p * 0.02

        if not in_position:
            # Entry condition: Uptrend (Close > EMA 200) + RSI in accumulation zone (40 - 58)
            if close_p > ema_200 and 40.0 <= rsi <= 58.0:
                in_position = True
                entry_price = close_p
                entry_date = date_str
                stop_loss = round(entry_price - (1.8 * atr), 2)
                target_price = round(entry_price + (2.5 * (entry_price - stop_loss)), 2)
        else:
            # Check exit triggers (Target Hit or Stop Loss Hit)
            exit_triggered = False
            exit_price = close_p
            reason = ""

            if low_p <= stop_loss:
                exit_triggered = True
                exit_price = stop_loss
                reason = "Stop Loss Hit"
            elif high_p >= target_price:
                exit_triggered = True
                exit_price = target_price
                reason = "Target Price Hit"
            elif rsi >= 75.0: # Overbought exit
                exit_triggered = True
                exit_price = close_p
                reason = "RSI Overbought Exit"

            if exit_triggered:
                ret_pct = round(((exit_price - entry_price) / entry_price) * 100, 2)
                trades.append({
                    "Ticker": ticker,
                    "Entry_Date": entry_date,
                    "Exit_Date": date_str,
                    "Entry_Price": round(entry_price, 2),
                    "Exit_Price": round(exit_price, 2),
                    "Return_Pct": ret_pct,
                    "Exit_Reason": reason
                })
                in_position = False

    # Calculate stock backtest metrics
    if trades:
        wins = [t for t in trades if t["Return_Pct"] > 0]
        win_rate = round((len(wins) / len(trades)) * 100, 1)
        total_return_pct = round(sum(t["Return_Pct"] for t in trades), 2)
    else:
        win_rate = 0.0
        total_return_pct = 0.0

    return {
        "ticker": ticker,
        "symbol": fun.get("name", ticker),
        "total_trades": len(trades),
        "win_rate": win_rate,
        "total_return_pct": total_return_pct,
        "trades": trades
    }

def run_full_universe_backtest(tickers=None):
    """Runs 1-Year Walk-Forward simulation across universe and aggregates performance."""
    if tickers is None:
        tickers = list(DEFAULT_KLSE_STOCKS.keys())

    all_trades = []
    stock_summaries = []

    for ticker in tickers:
        res = backtest_single_stock(ticker)
        all_trades.extend(res["trades"])
        stock_summaries.append({
            "Ticker": ticker,
            "Name": res.get("symbol", ticker)[:25],
            "Total Trades": res["total_trades"],
            "Win Rate (%)": f"{res['win_rate']}%",
            "Cumulative Return": f"{'+' if res['total_return_pct'] >= 0 else ''}{res['total_return_pct']}%"
        })

    # Portfolio level aggregates
    equity_curve = []
    exit_stats = {"Target Price Hit": 0, "Stop Loss Hit": 0, "RSI Overbought Exit": 0, "Other": 0}

    if all_trades:
        winning_trades = [t for t in all_trades if t["Return_Pct"] > 0]
        losing_trades = [t for t in all_trades if t["Return_Pct"] <= 0]

        win_rate = round((len(winning_trades) / len(all_trades)) * 100, 1)
        avg_trade_return = round(float(np.mean([t["Return_Pct"] for t in all_trades])), 2)
        total_portfolio_return = round(sum([t["Return_Pct"] for t in all_trades]), 2)
        profit_factor = round(
            sum([t["Return_Pct"] for t in winning_trades]) / (abs(sum([t["Return_Pct"] for t in losing_trades])) + 1e-9),
            2
        )

        # Chronological Equity Curve & Exit Stats
        sorted_trades = sorted(all_trades, key=lambda x: x.get("Exit_Date", ""))
        cum_ret = 0.0
        for t in sorted_trades:
            cum_ret += t["Return_Pct"]
            equity_curve.append({
                "date": t.get("Exit_Date", ""),
                "ticker": t.get("Ticker", ""),
                "trade_return": t["Return_Pct"],
                "cumulative_return": round(cum_ret, 2)
            })

            reason = t.get("Exit_Reason", "")
            if reason in exit_stats:
                exit_stats[reason] += 1
            else:
                exit_stats["Other"] += 1
    else:
        win_rate = 0.0
        avg_trade_return = 0.0
        total_portfolio_return = 0.0
        profit_factor = 0.0

    summary_metrics = {
        "Simulation Window": "1 Year Walk-Forward",
        "Total Universe Stocks": len(tickers),
        "Total Trades Executed": len(all_trades),
        "Win Rate": f"{win_rate}%",
        "Average Trade Return": f"{'+' if avg_trade_return >= 0 else ''}{avg_trade_return}%",
        "Cumulative Return": f"{'+' if total_portfolio_return >= 0 else ''}{total_portfolio_return}%",
        "Profit Factor": profit_factor
    }

    summary_df = pd.DataFrame(stock_summaries) if stock_summaries else pd.DataFrame()
    trades_df = pd.DataFrame(all_trades) if all_trades else pd.DataFrame()

    return summary_df, trades_df, summary_metrics, equity_curve, exit_stats

