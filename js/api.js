/* api.js - API Fetcher Module */

const API = {
  async scanLive(minFund, minRR, requireUptrend, fullMarket, portfolio = 'top50') {
    const url = `/api/live/scan?min_fund=${minFund}&min_rr=${minRR}&require_uptrend=${requireUptrend}&full_market=${fullMarket}&portfolio=${portfolio}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Scan API error: ${response.status}`);
    return await response.json();
  },

  async fetchStock(ticker) {
    const response = await fetch(`/api/live/stock/${ticker}`);
    if (!response.ok) throw new Error(`Stock API error: ${response.status}`);
    return await response.json();
  },

  async runBacktest() {
    const response = await fetch('/api/backtest/run');
    if (!response.ok) throw new Error(`Backtest API error: ${response.status}`);
    return await response.json();
  }
};
