"""
main.py - Terminal / CLI Engine for KLSE Quant Stock Recommendation & Backtesting.
Runs directly in any terminal with rich ASCII table output.
"""

import argparse
import sys
import pandas as pd
import numpy as np

from src.core.config import DEFAULT_KLSE_STOCKS
from src.data.fetcher import fetch_klse_stock_data
from src.engines.live_engine import run_live_scan, analyze_stock
from src.engines.backtest_engine import run_full_universe_backtest, backtest_single_stock

def format_ascii_table(df: pd.DataFrame, title: str = "") -> str:
    if title:
        out = f"\n========================================================================================\n"
        out += f"  {title.upper()}\n"
        out += f"========================================================================================\n"
    else:
        out = ""
    out += df.to_string(index=False)
    out += "\n----------------------------------------------------------------------------------------\n"
    return out

def run_terminal_scan(tickers=None, min_fund=60, require_uptrend=True, min_rr=2.0):
    if tickers is None:
        tickers = list(DEFAULT_KLSE_STOCKS.keys())

    print(f"\n🔍 Scanning {len(tickers)} KLSE stocks in terminal mode...\n")

    res = run_live_scan(tickers=tickers, min_fund=min_fund, require_uptrend=require_uptrend, min_rr=min_rr)
    results = res["results"]

    if results:
        formatted = []
        for r in results:
            formatted.append({
                "Ticker": r['ticker'],
                "Name": r['symbol'][:25],
                "Signal": r['recommendation'],
                "Price": f"MYR {r['current_price']:.2f}",
                "Entry (EP)": f"MYR {r['entry_price']:.2f}",
                "Target (TP)": f"MYR {r['target_price']:.2f}",
                "Stop (SL)": f"MYR {r['stop_loss']:.2f}",
                "Upside": f"+{r['upside_pct']}%",
                "R:R": r['risk_reward_ratio'],
                "Score": f"{r['quant_score']}"
            })
        res_df = pd.DataFrame(formatted)
        print(format_ascii_table(res_df, "QUANT SCANNER RECOMMENDATION MATRIX"))
    else:
        print("⚠️ No stocks matched your current criteria.")

def run_terminal_stock_inspect(ticker: str):
    print(f"\n🔍 Fetching deep-dive quant breakdown for {ticker}...\n")
    df, fun = fetch_klse_stock_data(ticker)
    res = analyze_stock(df, fun)

    print("========================================================================================")
    print(f"  STOCK BLUEPRINT: {res['symbol']} ({ticker})")
    print(f"  Sector: {res['sector']}")
    print("========================================================================================")
    print(f"  Current Market Price: MYR {res['current_price']:.2f}")
    print(f"  Signal / Action:      [{res['recommendation']}] - {res['action_note']}")
    print(f"  Overall Quant Score:  {res['quant_score']} / 100")
    print(f"  Fundamental Score:    {res['fundamental_score']} / 100")
    print(f"  Technical Score:      {res['technical_score']} / 100")
    print("----------------------------------------------------------------------------------------")
    print("  TRADE EXECUTION LEVELS:")
    print(f"    Suggested Entry (EP): MYR {res['entry_price']:.2f} ({res['entry_range']})")
    print(f"    Target Price (TP):    MYR {res['target_price']:.2f} (+{res['upside_pct']}%)")
    print(f"    Stop Loss (SL):       MYR {res['stop_loss']:.2f} (-{res['downside_pct']}%)")
    print(f"    Risk : Reward Ratio:  {res['risk_reward_ratio']}")
    print("----------------------------------------------------------------------------------------")
    print("  KEY METRICS BREAKDOWN:")
    for k, v in res['metrics'].items():
        print(f"    - {k:<20}: {v}")
    print("========================================================================================\n")

def run_terminal_backtest(tickers=None):
    if tickers is None:
        tickers = list(DEFAULT_KLSE_STOCKS.keys())

    print(f"\n🧪 Running 1-Year Walk-Forward Backtest on Terminal for {len(tickers)} stocks...\n")
    summary_df, trades_df, metrics = run_full_universe_backtest(tickers)

    print("========================================================================================")
    print("  1-YEAR HISTORICAL BACKTEST PORTFOLIO SUMMARY")
    print("========================================================================================")
    for k, v in metrics.items():
        print(f"  {k:<32}: {v}")
    print("----------------------------------------------------------------------------------------")

    if not summary_df.empty:
        print(format_ascii_table(summary_df, "PER-STOCK PERFORMANCE BREAKDOWN"))

    if not trades_df.empty:
        print(f"Recent Executed Trade Log (Total Trades: {len(trades_df)}):")
        print(format_ascii_table(trades_df.tail(10), "RECENT 10 TRADES"))

def interactive_menu():
    while True:
        print("\n" + "="*50)
        print("  📈 PLANT SOME STOCKS RECOMMENDATION ENGINE (TERMINAL)")
        print("="*50)
        print("  1. Run Live Scanner on KLSE Stock Universe")
        print("  2. Inspect Single Stock Blueprint")
        print("  3. Run 1-Year Historical Backtest Simulation")
        print("  4. Exit")
        print("="*50)

        choice = input("Select an option (1-4): ").strip()
        if choice == '1':
            run_terminal_scan()
        elif choice == '2':
            symbol = input("Enter KLSE Ticker Code (e.g. 1155.KL, 7084.KL, 1023.KL): ").strip()
            if symbol:
                run_terminal_stock_inspect(symbol)
        elif choice == '3':
            run_terminal_backtest()
        elif choice == '4':
            print("Exiting KLSE Quant Engine. Goodbye!")
            break
        else:
            print("Invalid option. Please enter 1, 2, 3, or 4.")

def main():
    parser = argparse.ArgumentParser(description="KLSE Terminal Stock Recommendation & Backtest Engine")
    parser.add_argument("--scan", action="store_true", help="Run live scanner on KLSE stock universe")
    parser.add_argument("--ticker", type=str, help="Deep dive analysis for a single ticker (e.g., 1155.KL)")
    parser.add_argument("--backtest", action="store_true", help="Run 1-year backtest simulation")
    
    args = parser.parse_args()

    if args.scan:
        run_terminal_scan()
    elif args.ticker:
        run_terminal_stock_inspect(args.ticker)
    elif args.backtest:
        run_terminal_backtest()
    else:
        interactive_menu()

if __name__ == "__main__":
    main()