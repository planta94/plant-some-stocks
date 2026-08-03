"""
live_engine.py - Live Quantitative Stock Recommendation & Blueprint Engine.
Evaluates stock market fundamentals + technicals with an Early Exit Fast-Gatekeeper and Signal Reasoning Generator.
"""

import pandas as pd
import numpy as np
from src.engines.indicators import calculate_technical_indicators
from src.data.fetcher import fetch_klse_stock_data, _safe_float
from src.core.config import DEFAULT_KLSE_STOCKS, get_full_klse_universe

def fast_pass_gatekeeper(df: pd.DataFrame, require_uptrend: bool = True) -> tuple[bool, str]:
    """
    Early Exit Filter: Rapidly screens stock before expensive analysis.
    Returns (is_qualified, rejection_reason).
    """
    if df.empty or len(df) < 50:
        return False, "Insufficient Data History"

    latest = df.iloc[-1]
    cmp = _safe_float(latest['Close'])

    # 1. Price Sanity & Liquidity Filter (Skip dead illiquid / penny stocks)
    if cmp < 0.10:
        return False, "Penny Stock (< MYR 0.10)"

    recent_vol = _safe_float(df['Volume'].iloc[-20:].mean())
    if recent_vol < 10000:
        return False, "Illiquid Stock (Avg Vol < 10k)"

    # 2. Macro Trend Gatekeeper (Early check for EMA 200)
    if require_uptrend:
        close_series = df['Close']
        if isinstance(close_series, pd.DataFrame):
            close_series = close_series.iloc[:, 0]
        ema_200 = _safe_float(close_series.ewm(span=200, adjust=False).mean().iloc[-1])
        if cmp < ema_200:
            return False, "Macro Downtrend (Price < EMA 200)"

    return True, "Passed Pre-Filter"

def analyze_stock(df: pd.DataFrame, fundamentals: dict) -> dict:
    """Analyzes price history and fundamentals to output trade blueprint, scores, and detailed reasoning justification."""
    df_calc = calculate_technical_indicators(df)
    latest = df_calc.iloc[-1]
    cmp = _safe_float(latest['Close'])

    # 1. Fundamental Scoring (Max 100)
    roe = _safe_float(fundamentals.get("roe"), default=10.0)
    pe = _safe_float(fundamentals.get("pe_ratio"), default=15.0)
    pb = _safe_float(fundamentals.get("pb_ratio"), default=1.2)
    de = _safe_float(fundamentals.get("debt_to_equity"), default=50.0)
    div_yield = _safe_float(fundamentals.get("dividend_yield"), default=3.0)

    f_score = 0
    f_reasons = []

    if roe >= 12.0:
        f_score += 25
        f_reasons.append(f"High Profitability: ROE of {roe}% exceeds 12.0% benchmark")
    elif roe >= 8.0:
        f_score += 15
        f_reasons.append(f"Moderate Profitability: ROE of {roe}% is in acceptable range")
    else:
        f_score += 5
        f_reasons.append(f"Lower Profitability: ROE of {roe}% is below 8.0%")

    if 5.0 <= pe <= 18.0:
        f_score += 25
        f_reasons.append(f"Attractive Valuation: P/E Ratio of {pe}x is in value zone (5-18x)")
    elif 18.0 < pe <= 28.0:
        f_score += 15
        f_reasons.append(f"Fair Valuation: P/E Ratio of {pe}x reflects moderate growth expectation")
    else:
        f_score += 5
        f_reasons.append(f"High Valuation / Special Case: P/E Ratio of {pe}x")

    if pb <= 1.8:
        f_score += 15
        f_reasons.append(f"Solid Book Value: Price-to-Book ratio of {pb}x is under 1.8x")
    elif pb <= 3.0:
        f_score += 10

    if de <= 60.0:
        f_score += 20
        f_reasons.append(f"Healthy Balance Sheet: Low Debt-to-Equity ratio of {de}%")
    elif de <= 120.0:
        f_score += 10

    if div_yield >= 4.0:
        f_score += 15
        f_reasons.append(f"High Income Support: Dividend Yield of {div_yield}% provides downside buffer")
    elif div_yield >= 2.0:
        f_score += 10

    fundamental_score = min(100, f_score)

    # 2. Technical Scoring (Max 100)
    ema_20 = _safe_float(latest['EMA_20'], default=cmp)
    ema_50 = _safe_float(latest['EMA_50'], default=cmp)
    ema_200 = _safe_float(latest['EMA_200'], default=cmp)
    rsi = _safe_float(latest['RSI_14'], default=50.0)
    atr = _safe_float(latest['ATR_14'], default=cmp * 0.02)
    macd_hist = _safe_float(latest['MACD_Hist'], default=0.0)

    t_score = 0
    t_reasons = []

    if cmp > ema_200:
        t_score += 30
        t_reasons.append(f"Macro Uptrend: Market price (MYR {cmp:.2f}) trades above 200-day EMA (MYR {ema_200:.2f})")
    else:
        t_reasons.append(f"Macro Downtrend: Market price (MYR {cmp:.2f}) trades below 200-day EMA (MYR {ema_200:.2f})")

    if cmp > ema_50:
        t_score += 20
        t_reasons.append(f"Intermediate Support: Price holds above 50-day EMA (MYR {ema_50:.2f})")
    if ema_50 > ema_200:
        t_score += 15
        t_reasons.append("Golden Alignment: 50-day EMA is stacked above 200-day EMA")

    if 40.0 <= rsi <= 60.0:
        t_score += 20
        t_reasons.append(f"Accumulation Zone: RSI (14) at {rsi:.1f} indicates healthy pullback without panic selling")
    elif 30.0 <= rsi < 40.0:
        t_score += 15
        t_reasons.append(f"Oversold Value Area: RSI (14) at {rsi:.1f} shows potential rebound entry")

    if macd_hist > 0:
        t_score += 15
        t_reasons.append("Positive Momentum: MACD histogram is positive")

    technical_score = min(100, t_score)
    quant_score = round(0.5 * fundamental_score + 0.5 * technical_score, 1)

    # 3. EP, TP, SL Level Calculations
    swing_low_20 = _safe_float(latest['Low_20'], default=cmp * 0.95)
    volatility_sl = cmp - (1.8 * atr)
    technical_support = min(swing_low_20, ema_50)

    sl_raw = min(technical_support, volatility_sl)
    sl_price = round(float(np.clip(sl_raw, cmp * 0.88, cmp * 0.97)), 2)

    risk_amount = cmp - sl_price
    if risk_amount <= 0.01:
        risk_amount = round(cmp * 0.05, 2)
        sl_price = round(cmp - risk_amount, 2)

    ep_low = round(min(cmp, max(sl_price + 0.01, ema_20 * 0.995)), 2)
    ep_high = round(cmp, 2)
    ep_price = round(cmp, 2)

    fifty_two_high = _safe_float(fundamentals.get("fifty_two_week_high"), default=cmp * 1.25)
    rr_target_tp = ep_price + (2.5 * risk_amount)
    tp_price = round(max(rr_target_tp, min(fifty_two_high, ep_price + (3.0 * risk_amount))), 2)

    reward_amount = tp_price - ep_price
    rr_ratio = round(reward_amount / risk_amount, 2) if risk_amount > 0 else 2.0

    upside_pct = round(((tp_price - ep_price) / ep_price) * 100, 2)
    downside_pct = round(((ep_price - sl_price) / ep_price) * 100, 2)

    # 4. Recommendation Signals & Detailed Reasoning
    if quant_score >= 72 and cmp > ema_200 and rr_ratio >= 2.0:
        recommendation = "STRONG BUY"
        action_note = "High conviction setup. Solid fundamentals with healthy technical pullback."
    elif quant_score >= 60 and cmp > ema_200:
        recommendation = "BUY"
        action_note = "Favorable risk-reward. Good long-term trend alignment."
    elif quant_score >= 50:
        recommendation = "HOLD / ACCUMULATE ON DIP"
        action_note = "Consolidating. Wait for pullback closer to Entry Price."
    else:
        recommendation = "AVOID / WATCH"
        action_note = "Below key trendlines or weaker fundamental metrics."

    rr_reason = f"Entry at MYR {ep_price:.2f} targets MYR {tp_price:.2f} (+{upside_pct}%) with Stop Loss at MYR {sl_price:.2f} (-{downside_pct}%), securing a {rr_ratio}x Risk:Reward ratio."

    reasoning_payload = {
        "summary": f"Rated [{recommendation}] with overall Quant Score of {quant_score} (Fundamental: {fundamental_score}, Technical: {technical_score}).",
        "fundamental_reasons": f_reasons,
        "technical_reasons": t_reasons,
        "risk_reward_reason": rr_reason
    }

    # Format chart data for frontend charting libraries (e.g. ApexCharts)
    chart_series = []
    tail_df = df_calc.tail(100)
    for idx, row in tail_df.iterrows():
        chart_series.append({
            "date": str(idx)[:10],
            "open": round(_safe_float(row["Open"]), 2),
            "high": round(_safe_float(row["High"]), 2),
            "low": round(_safe_float(row["Low"]), 2),
            "close": round(_safe_float(row["Close"]), 2),
            "volume": int(_safe_float(row["Volume"])),
            "ema20": round(_safe_float(row["EMA_20"]), 2),
            "ema50": round(_safe_float(row["EMA_50"]), 2),
            "ema200": round(_safe_float(row["EMA_200"]), 2),
            "rsi": round(_safe_float(row["RSI_14"], default=50.0), 1),
            "macd": round(_safe_float(row["MACD_Hist"], default=0.0), 3),
        })

    return {
        "symbol": str(fundamentals.get("name")),
        "sector": str(fundamentals.get("sector")),
        "current_price": cmp,
        "recommendation": recommendation,
        "action_note": action_note,
        "reasoning": reasoning_payload,
        "quant_score": quant_score,
        "fundamental_score": fundamental_score,
        "technical_score": technical_score,
        "entry_price": ep_price,
        "entry_range": f"MYR {ep_low:.2f} - MYR {ep_high:.2f}",
        "target_price": tp_price,
        "stop_loss": sl_price,
        "risk_reward_ratio": f"1 : {rr_ratio}",
        "upside_pct": upside_pct,
        "downside_pct": downside_pct,
        "metrics": {
            "ROE (%)": roe,
            "P/E Ratio": pe,
            "P/B Ratio": pb,
            "Debt/Equity (%)": de,
            "Div Yield (%)": div_yield,
            "RSI (14)": round(rsi, 1),
            "EMA 50": round(ema_50, 2),
            "EMA 200": round(ema_200, 2),
            "ATR (14)": round(atr, 2)
        },
        "chart_data": chart_series
    }

def run_live_scan(tickers=None, min_fund=60.0, require_uptrend=True, min_rr=2.0, use_full_universe=False):
    """Scans the KLSE stock universe with an Early Exit Fast-Gatekeeper for ultra-fast scanning."""
    if tickers is None:
        if use_full_universe:
            tickers = list(get_full_klse_universe().keys())
        else:
            tickers = list(DEFAULT_KLSE_STOCKS.keys())

    scanned_results = []
    skipped_count = 0

    for ticker in tickers:
        try:
            df, fun = fetch_klse_stock_data(ticker)
            
            # Stage 1: Fast-Pass Early Exit Gatekeeper
            is_qualified, reason = fast_pass_gatekeeper(df, require_uptrend=require_uptrend)
            if not is_qualified:
                skipped_count += 1
                continue

            # Stage 2: Deep Analysis for qualified stocks
            res = analyze_stock(df, fun)
            res['ticker'] = ticker

            cond_fund = res['fundamental_score'] >= min_fund
            rr_num = float(res['risk_reward_ratio'].split(":")[-1].strip())
            cond_rr = rr_num >= min_rr

            if cond_fund and cond_rr:
                scanned_results.append({
                    "ticker": ticker,
                    "symbol": res['symbol'],
                    "sector": res['sector'],
                    "recommendation": res['recommendation'],
                    "action_note": res['action_note'],
                    "reasoning": res['reasoning'],
                    "current_price": res['current_price'],
                    "entry_price": res['entry_price'],
                    "target_price": res['target_price'],
                    "stop_loss": res['stop_loss'],
                    "upside_pct": res['upside_pct'],
                    "downside_pct": res['downside_pct'],
                    "risk_reward_ratio": res['risk_reward_ratio'],
                    "quant_score": res['quant_score'],
                    "fundamental_score": res['fundamental_score'],
                    "technical_score": res['technical_score']
                })
        except Exception as err:
            print(f"Error scanning {ticker}: {err}")
            skipped_count += 1
            continue

    return {
        "total_scanned": len(tickers),
        "early_exit_skipped": skipped_count,
        "matched_count": len(scanned_results),
        "results": scanned_results
    }
