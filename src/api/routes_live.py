"""
routes_live.py - API routes for live stock scanning and deep-dive blueprint analysis.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from src.engines.live_engine import run_live_scan, analyze_stock
from src.data.fetcher import fetch_klse_stock_data
from src.core.models import ScanResponse, StockBlueprintResponse, ScanRequest

router = APIRouter(prefix="/api/live", tags=["Live Recommendations"])

@router.get("/scan", response_model=ScanResponse)
def scan_live_stocks(
    min_fund: float = Query(60.0, description="Minimum Fundamental score (0-100)"),
    require_uptrend: bool = Query(True, description="Filter for price >= EMA 200"),
    min_rr: float = Query(2.0, description="Minimum Risk to Reward Ratio"),
    full_market: bool = Query(False, description="Scan entire Bursa Malaysia Market (~1000 stocks)")
):
    """Executes live scanner across KLSE stock universe."""
    res = run_live_scan(
        min_fund=min_fund,
        require_uptrend=require_uptrend,
        min_rr=min_rr,
        use_full_universe=full_market
    )
    return res

@router.post("/scan", response_model=ScanResponse)
def scan_live_stocks_post(payload: ScanRequest):
    """Executes live scanner with custom ticker selection and parameters."""
    res = run_live_scan(
        tickers=payload.tickers,
        min_fund=payload.min_fund,
        require_uptrend=payload.require_uptrend,
        min_rr=payload.min_rr
    )
    return res

@router.get("/stock/{ticker}", response_model=StockBlueprintResponse)
def inspect_stock(ticker: str):
    """Fetches full stock blueprint, scores, EP/TP/SL trade setup, and chart data."""
    df, fun = fetch_klse_stock_data(ticker)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Stock ticker '{ticker}' not found or data unavailable.")
    
    res = analyze_stock(df, fun)
    res['ticker'] = ticker
    return res
