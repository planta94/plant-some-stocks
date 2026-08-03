# 📈 Plant Some Stocks - KLSE Quant Recommendation Engine & Simulation Platform

A scalable, modular quantitative analysis platform for **Bursa Malaysia (KLSE)** stocks. Features dual modes: **⚡ Live Market Recommendations** and **🧪 1-Year Walk-Forward Backtest Simulations**.

---

## 🏗 Project Architecture (`src/` Package)

```
plant-some-stocks/
├── Dockerfile                  # Production container definition
├── docker-compose.yml          # Container orchestration (port 8000)
├── requirements.txt            # Python dependencies
├── server.py                   # FastAPI application server launcher
├── main.py                     # CLI terminal application launcher
├── export_static.py            # Static HTML builder for GH / Google Pages
│
└── src/                        # Modular Core Application
    ├── core/                   # Stock universe config & Pydantic models
    ├── data/                   # yfinance market data fetcher with mock fallback
    ├── engines/                # Dual Engines:
    │   ├── indicators.py       # Technical indicators (EMA 20/50/200, RSI, MACD, ATR)
    │   ├── live_engine.py      # ⚡ Live market scanner & trade setup builder
    │   └── backtest_engine.py  # 🧪 Walk-forward historical backtest simulation
    ├── api/                    # REST API routes (/api/live, /api/backtest)
    └── static/                 # Glassmorphism Dark-Mode Web Dashboard UI
        ├── index.html
        ├── css/style.css
        └── js/app.js
```

---

## 🚀 Quickstart Guide

### 1. Run with Docker Compose (Recommended)
Launch the unified FastAPI server and Web App in a container:
```bash
docker compose up --build
```
Access the interactive web dashboard at: `http://localhost:8000`

---

### 2. Run Locally (Python)
Install dependencies and launch the server:
```bash
pip install -r requirements.txt
python server.py
```
Open your browser at `http://localhost:8000`.

---

### 3. Run in Terminal / CLI Mode
If you prefer CLI operation:
```bash
# Run live scanner in terminal
python main.py --scan

# Inspect a single stock ticker blueprint
python main.py --ticker 1155.KL

# Run terminal backtest simulation
python main.py --backtest
```

---

### 4. Deploy to GitHub Pages / Google Pages
Build a zero-backend static web bundle in `dist/`:
```bash
python export_static.py
```
Push the contents of `dist/` to GitHub Pages, Google Cloud Storage, or any static host!
