"""
routes_universe.py - API route to list available KLSE stock universe and thematic portfolios.
"""

from fastapi import APIRouter
from src.core.config import DEFAULT_KLSE_STOCKS, THEMATIC_PORTFOLIOS

router = APIRouter(prefix="/api/universe", tags=["Universe Config"])

@router.get("")
def get_universe():
    """Returns list of monitored KLSE stocks and metadata."""
    universe_list = []
    for ticker, info in DEFAULT_KLSE_STOCKS.items():
        universe_list.append({
            "ticker": ticker,
            "name": info["name"],
            "sector": info["sector"]
        })
    return {"total": len(universe_list), "stocks": universe_list}

@router.get("/portfolios")
def get_portfolios():
    """Returns list of available thematic portfolios and strategy descriptions."""
    return {"portfolios": THEMATIC_PORTFOLIOS}
