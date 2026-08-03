"""
routes_backtest.py - API routes for 1-year walk-forward backtest simulations.
"""

from fastapi import APIRouter
from src.engines.backtest_engine import run_full_universe_backtest
from src.core.models import BacktestResponse, BacktestRequest

router = APIRouter(prefix="/api/backtest", tags=["Simulation & Backtesting"])

@router.get("/run", response_model=BacktestResponse)
def run_backtest_get():
    """Runs 1-year historical simulation on default KLSE universe."""
    summary_df, trades_df, summary_metrics = run_full_universe_backtest()
    
    stock_breakdown = summary_df.to_dict(orient="records") if not summary_df.empty else []
    recent_trades = trades_df.to_dict(orient="records") if not trades_df.empty else []
    
    return {
        "summary_metrics": summary_metrics,
        "stock_breakdown": stock_breakdown,
        "recent_trades": recent_trades
    }

@router.post("/run", response_model=BacktestResponse)
def run_backtest_post(payload: BacktestRequest):
    """Runs 1-year historical simulation on custom selected tickers."""
    summary_df, trades_df, summary_metrics = run_full_universe_backtest(tickers=payload.tickers)
    
    stock_breakdown = summary_df.to_dict(orient="records") if not summary_df.empty else []
    recent_trades = trades_df.to_dict(orient="records") if not trades_df.empty else []
    
    return {
        "summary_metrics": summary_metrics,
        "stock_breakdown": stock_breakdown,
        "recent_trades": recent_trades
    }
