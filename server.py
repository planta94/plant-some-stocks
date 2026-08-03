"""
server.py - FastAPI Application Server Entrypoint.
Serves REST API endpoints and static dark-mode web application.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from src.api.routes_live import router as live_router
from src.api.routes_backtest import router as backtest_router
from src.api.routes_universe import router as universe_router

app = FastAPI(
    title="Plant Some Stocks",
    description="Scalable quantitative stock scanner, trade blueprint builder, and walk-forward backtest platform.",
    version="1.0.0"
)

# Enable CORS for external frontend or local testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(live_router)
app.include_router(backtest_router)
app.include_router(universe_router)

# Mount Static Files UI directory
static_dir = os.path.join(os.path.dirname(__file__), "src", "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
