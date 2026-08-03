/* backtest.js - Live Backtest Simulation Controller & Analytics Module */

let btProgressInterval = null;
let equityChart = null;
let exitChart = null;
let cachedBacktestData = null;

async function runBacktestSimulation() {
  const btReturn = document.getElementById("bt-kpi-return");
  const btWinrate = document.getElementById("bt-kpi-winrate");
  const btPF = document.getElementById("bt-kpi-pf");
  const btTrades = document.getElementById("bt-kpi-trades");

  if (btReturn) btReturn.innerText = "Running...";
  if (btWinrate) btWinrate.innerText = "--";
  if (btPF) btPF.innerText = "--";
  if (btTrades) btTrades.innerText = "--";

  // Start progress animation
  showProgressMonitor("Running 1-Year Walk-Forward Simulation...", "Executing live daily simulation across KLSE universe...");
  let currProgress = 10;
  clearInterval(btProgressInterval);
  btProgressInterval = setInterval(() => {
    if (currProgress < 90) {
      currProgress += Math.random() * 14 + 6;
      updateProgressMonitor(currProgress, "Simulating position entries & exit triggers...", `${Math.round(currProgress)}%`);
    }
  }, 200);
  
  try {
    const data = await API.runBacktest();
    clearInterval(btProgressInterval);
    completeProgressMonitor("1-Year Backtest Simulation Complete!", 100);
    cachedBacktestData = data;
    renderBacktestDashboard(data);
  } catch (err) {
    clearInterval(btProgressInterval);
    document.getElementById("progress-card").classList.add("hidden");
    
    if (btReturn) btReturn.innerText = "Error";
    if (btWinrate) btWinrate.innerText = "Error";
    if (btPF) btPF.innerText = "Error";
    if (btTrades) btTrades.innerText = "Error";

    const stockBody = document.getElementById("bt-stock-table-body");
    if (stockBody) {
      stockBody.innerHTML = `<tr><td colspan="5" class="text-center text-red font-semibold"><i class="fa-solid fa-triangle-exclamation"></i> ${err.message}</td></tr>`;
    }

    const tradesBody = document.getElementById("bt-trades-table-body");
    if (tradesBody) {
      tradesBody.innerHTML = `<tr><td colspan="7" class="text-center text-red font-semibold"><i class="fa-solid fa-triangle-exclamation"></i> Live API unavailable. Ensure backend server is running on port 8000.</td></tr>`;
    }

    console.error("Live Backtest Engine API Failure:", err);
  }
}

function renderBacktestDashboard(data) {
  if (!data) return;
  const metrics = data.summary_metrics || {};

  const btReturn = document.getElementById("bt-kpi-return");
  const btWinrate = document.getElementById("bt-kpi-winrate");
  const btPF = document.getElementById("bt-kpi-pf");
  const btTrades = document.getElementById("bt-kpi-trades");

  if (btReturn) btReturn.innerText = metrics["Cumulative Return"] || "0.0%";
  if (btWinrate) btWinrate.innerText = metrics["Win Rate"] || "0.0%";
  if (btPF) btPF.innerText = metrics["Profit Factor"] || "0.0";
  if (btTrades) btTrades.innerText = metrics["Total Trades Executed"] || "0";

  // Render Charts
  if (data.equity_curve && data.equity_curve.length > 0) {
    renderEquityCurveChart(data.equity_curve);
  } else if (data.recent_trades && data.recent_trades.length > 0) {
    let cum = 0;
    const curve = data.recent_trades.map(t => {
      cum += t.Return_Pct;
      return { date: t.Exit_Date, cumulative_return: Math.round(cum * 100) / 100 };
    });
    renderEquityCurveChart(curve);
  }

  if (data.exit_stats) {
    renderExitReasonChart(data.exit_stats);
  } else if (data.recent_trades && data.recent_trades.length > 0) {
    const stats = {};
    data.recent_trades.forEach(t => {
      const r = t.Exit_Reason || "Other";
      stats[r] = (stats[r] || 0) + 1;
    });
    renderExitReasonChart(stats);
  }

  // Stock Breakdown Table
  renderStockBreakdownTable(data.stock_breakdown || []);

  // Trade Execution Log Table
  renderTradesLogTable(data.recent_trades || []);
}

function renderStockBreakdownTable(stocks) {
  const stockBody = document.getElementById("bt-stock-table-body");
  if (!stockBody) return;

  let sHtml = "";
  stocks.forEach(row => {
    const rawWin = parseFloat(row["Win Rate (%)"]) || 0;
    let winClass = "text-muted";
    if (rawWin >= 50) winClass = "text-green";
    else if (rawWin >= 40) winClass = "text-gold";

    const isRetPositive = (row["Cumulative Return"] || "").includes("+");
    const retClass = isRetPositive ? "text-green" : "text-red";

    sHtml += `
      <tr>
        <td class="font-mono font-bold">${row.Ticker}</td>
        <td class="font-semibold">${row.Name}</td>
        <td class="font-mono">${row["Total Trades"]}</td>
        <td class="${winClass} font-mono font-bold">${row["Win Rate (%)"]}</td>
        <td class="${retClass} font-mono font-bold">${row["Cumulative Return"]}</td>
      </tr>
    `;
  });
  stockBody.innerHTML = sHtml || `<tr><td colspan="5" class="text-center">No backtest breakdown available.</td></tr>`;
}

function renderTradesLogTable(trades) {
  const tradesBody = document.getElementById("bt-trades-table-body");
  if (!tradesBody) return;

  let tHtml = "";
  trades.slice(-25).reverse().forEach(t => {
    const isProfit = t.Return_Pct > 0;
    const badgeHtml = getExitBadge(t.Exit_Reason || "");

    tHtml += `
      <tr>
        <td class="font-mono font-bold">${t.Ticker}</td>
        <td class="font-mono text-muted">${t.Entry_Date}</td>
        <td class="font-mono text-muted">${t.Exit_Date}</td>
        <td class="font-mono">MYR ${typeof t.Entry_Price === 'number' ? t.Entry_Price.toFixed(2) : t.Entry_Price}</td>
        <td class="font-mono">MYR ${typeof t.Exit_Price === 'number' ? t.Exit_Price.toFixed(2) : t.Exit_Price}</td>
        <td class="font-mono font-bold ${isProfit ? 'text-green' : 'text-red'}">${isProfit ? '+' : ''}${t.Return_Pct}%</td>
        <td>${badgeHtml}</td>
      </tr>
    `;
  });
  tradesBody.innerHTML = tHtml || `<tr><td colspan="7" class="text-center">No trades logged yet.</td></tr>`;
}

function getExitBadge(reason) {
  if (reason.includes("Target")) return `<span class="badge badge-target"><i class="fa-solid fa-bullseye"></i> ${reason}</span>`;
  if (reason.includes("Stop")) return `<span class="badge badge-stoploss"><i class="fa-solid fa-shield-xmark"></i> ${reason}</span>`;
  if (reason.includes("RSI") || reason.includes("Overbought")) return `<span class="badge badge-overbought"><i class="fa-solid fa-chart-line"></i> ${reason}</span>`;
  return `<span class="badge badge-hold">${reason}</span>`;
}

function filterStockTable(query) {
  if (!cachedBacktestData || !cachedBacktestData.stock_breakdown) return;
  const q = query.toLowerCase();
  const filtered = cachedBacktestData.stock_breakdown.filter(s => 
    s.Ticker.toLowerCase().includes(q) || s.Name.toLowerCase().includes(q)
  );
  renderStockBreakdownTable(filtered);
}

function filterTradesTable(query) {
  if (!cachedBacktestData || !cachedBacktestData.recent_trades) return;
  const q = query.toLowerCase();
  const filtered = cachedBacktestData.recent_trades.filter(t => 
    t.Ticker.toLowerCase().includes(q) || (t.Exit_Reason || "").toLowerCase().includes(q)
  );
  renderTradesLogTable(filtered);
}

function renderEquityCurveChart(seriesData) {
  const chartElement = document.querySelector("#bt-equity-chart");
  if (!chartElement) return;
  chartElement.innerHTML = "";

  const dates = seriesData.map(d => d.date);
  const returns = seriesData.map(d => d.cumulative_return);

  const options = {
    series: [{
      name: 'Cumulative Return (%)',
      data: returns
    }],
    chart: {
      type: 'area',
      height: 240,
      background: 'transparent',
      toolbar: { show: false }
    },
    stroke: { curve: 'smooth', width: 2 },
    fill: {
      type: 'gradient',
      gradient: {
        shadeIntensity: 1,
        opacityFrom: 0.4,
        opacityTo: 0.05,
        stops: [0, 90, 100]
      }
    },
    colors: ['#06b6d4'],
    theme: { mode: 'dark' },
    xaxis: { categories: dates, labels: { style: { colors: '#94a3b8', fontSize: '10px' } } },
    yaxis: { labels: { formatter: (val) => `${val >= 0 ? '+' : ''}${val.toFixed(1)}%`, style: { colors: '#94a3b8' } } },
    grid: { borderColor: 'rgba(255, 255, 255, 0.05)' }
  };

  if (equityChart) equityChart.destroy();
  equityChart = new ApexCharts(chartElement, options);
  equityChart.render();
}

function renderExitReasonChart(exitStats) {
  const chartElement = document.querySelector("#bt-exit-chart");
  if (!chartElement) return;
  chartElement.innerHTML = "";

  const labels = Object.keys(exitStats || {});
  const series = Object.values(exitStats || {});

  const options = {
    series: series.length > 0 ? series : [0, 0, 0],
    labels: labels.length > 0 ? labels : ['Target Price Hit', 'Stop Loss Hit', 'RSI Overbought Exit'],
    chart: {
      type: 'donut',
      height: 240,
      background: 'transparent'
    },
    colors: ['#10b981', '#ef4444', '#8b5cf6', '#f59e0b'],
    theme: { mode: 'dark' },
    legend: { position: 'bottom', labels: { colors: '#94a3b8' } },
    stroke: { show: false }
  };

  if (exitChart) exitChart.destroy();
  exitChart = new ApexCharts(chartElement, options);
  exitChart.render();
}
