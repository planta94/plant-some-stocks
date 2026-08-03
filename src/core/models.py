"""
models.py - Pydantic models for request/response payloads across API endpoints.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SignalReasoning(BaseModel):
    summary: str
    fundamental_reasons: List[str]
    technical_reasons: List[str]
    risk_reward_reason: str

class ScanRequest(BaseModel):
    tickers: Optional[List[str]] = None
    min_fund: float = Field(default=60.0, description="Minimum Fundamental Score threshold")
    require_uptrend: bool = Field(default=True, description="Require price >= EMA 200")
    min_rr: float = Field(default=2.0, description="Minimum Risk:Reward Ratio threshold")

class ScanItem(BaseModel):
    ticker: str
    symbol: str
    sector: str
    recommendation: str
    action_note: str
    reasoning: Optional[SignalReasoning] = None
    current_price: float
    entry_price: float
    target_price: float
    stop_loss: float
    upside_pct: float
    downside_pct: float
    risk_reward_ratio: str
    quant_score: float
    fundamental_score: float
    technical_score: float

class ScanResponse(BaseModel):
    total_scanned: int
    early_exit_skipped: Optional[int] = 0
    matched_count: int
    results: List[ScanItem]

class StockBlueprintResponse(BaseModel):
    ticker: str
    symbol: str
    sector: str
    current_price: float
    recommendation: str
    action_note: str
    reasoning: Optional[SignalReasoning] = None
    quant_score: float
    fundamental_score: float
    technical_score: float
    entry_price: float
    entry_range: str
    target_price: float
    stop_loss: float
    risk_reward_ratio: str
    upside_pct: float
    downside_pct: float
    metrics: Dict[str, Any]
    chart_data: Optional[List[Dict[str, Any]]] = None

class BacktestRequest(BaseModel):
    tickers: Optional[List[str]] = None

class TradeLogItem(BaseModel):
    Ticker: str
    Entry_Date: str
    Exit_Date: str
    Entry_Price: float
    Exit_Price: float
    Return_Pct: float
    Exit_Reason: str

class BacktestResponse(BaseModel):
    summary_metrics: Dict[str, Any]
    stock_breakdown: List[Dict[str, Any]]
    recent_trades: List[Dict[str, Any]]
