/* app.js - Main Application Coordinator */

document.addEventListener("DOMContentLoaded", () => {
  runLiveScan();
});

function switchTab(tabName) {
  document.querySelectorAll(".tab-content").forEach(el => el.classList.remove("active"));
  document.querySelectorAll(".nav-tab-btn").forEach(el => el.classList.remove("active"));

  if (tabName === 'live') {
    document.getElementById("tab-live").classList.add("active");
    document.getElementById("nav-live-btn").classList.add("active");
  } else if (tabName === 'backtest') {
    document.getElementById("tab-backtest").classList.add("active");
    document.getElementById("nav-backtest-btn").classList.add("active");
    if (typeof cachedBacktestData === 'undefined' || !cachedBacktestData) {
      runBacktestSimulation();
    }
  }
}

