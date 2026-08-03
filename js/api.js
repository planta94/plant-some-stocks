/* api.js - Live API Fetcher Module */

const API = {
  getApiUrl(path) {
    const cleanPath = path.startsWith('/') ? path.substring(1) : path;
    if (window.API_BASE_URL) {
      return `${window.API_BASE_URL.replace(/\/$/, '')}/${cleanPath}`;
    }
    // Relative URL resolution without forcing hardcoded root slash
    return cleanPath;
  },

  async scanLive(minFund, minRR, requireUptrend, fullMarket, portfolio = 'top50') {
    const url = this.getApiUrl(`api/live/scan?min_fund=${minFund}&min_rr=${minRR}&require_uptrend=${requireUptrend}&full_market=${fullMarket}&portfolio=${portfolio}`);
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Scan API Error (${response.status}): Failed to execute live quantitative scan.`);
    return await response.json();
  },

  async fetchStock(ticker) {
    const url = this.getApiUrl(`api/live/stock/${ticker}`);
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Stock API Error (${response.status}): Failed to fetch blueprint for ${ticker}.`);
    return await response.json();
  },

  async runBacktest() {
    const url = this.getApiUrl('api/backtest/run');
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Backtest API Error (${response.status}): Live backtest endpoint unreachable at ${url}.`);
    return await response.json();
  }
};
