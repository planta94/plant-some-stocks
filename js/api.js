/* api.js - API Fetcher Module */

const API = {
  getApiUrl(path) {
    // Standard relative URL path
    return path.startsWith('/') ? path : `/${path}`;
  },

  async scanLive(minFund, minRR, requireUptrend, fullMarket, portfolio = 'top50') {
    const url = this.getApiUrl(`api/live/scan?min_fund=${minFund}&min_rr=${minRR}&require_uptrend=${requireUptrend}&full_market=${fullMarket}&portfolio=${portfolio}`);
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Scan API error: ${response.status}`);
    return await response.json();
  },

  async fetchStock(ticker) {
    const url = this.getApiUrl(`api/live/stock/${ticker}`);
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Stock API error: ${response.status}`);
    return await response.json();
  },

  async runBacktest() {
    const url = this.getApiUrl('api/backtest/run');
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Backtest API error: ${response.status}`);
    return await response.json();
  }
};

