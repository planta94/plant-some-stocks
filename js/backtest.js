/* backtest.js - Backtest Simulation Controller Module */

let btProgressInterval = null;

async function runBacktestSimulation() {
  const btReturn = document.getElementById("bt-kpi-return");
  const btWinrate = document.getElementById("bt-kpi-winrate");
  const btPF = document.getElementById("bt-kpi-pf");
  const btTrades = document.getElementById("bt-kpi-trades");

  btReturn.innerText = "Running...";

  // Start progress animation
  showProgressMonitor("Running 1-Year Walk-Forward Simulation...", "Simulating daily trading history...");
  let currProgress = 10;
  clearInterval(btProgressInterval);
  btProgressInterval = setInterval(() => {
    if (currProgress < 90) {
      currProgress += Math.random() * 10 + 5;
      updateProgressMonitor(currProgress, "Simulating position entries & exit triggers...", `${Math.round(currProgress)}%`);
    }
  }, 300);
  
  try {
    const data = await API.runBacktest();
    clearInterval(btProgressInterval);
    completeProgressMonitor("1-Year Backtest Simulation Complete!", 100);

    btReturn.innerText = data.summary_metrics["Cumulative Return"] || "0.0%";
    btWinrate.innerText = data.summary_metrics["Win Rate"] || "0.0%";
    btPF.innerText = data.summary_metrics["Profit Factor"] || "0.0";
    btTrades.innerText = data.summary_metrics["Total Trades Executed"] || "0";

    // Stock Breakdown
    const stockBody = document.getElementById("bt-stock-table-body");
    let sHtml = "";
    (data.stock_breakdown || []).forEach(row => {
      sHtml += `
        <tr>
          <td class="font-mono font-bold">${row.Ticker}</td>
          <td>${row.Name}</td>
          <td>${row["Total Trades"]}</td>
          <td class="text-gold font-mono">${row["Win Rate (%)"]}</td>
          <td class="text-green font-mono">${row["Cumulative Return"]}</td>
        </tr>
      `;
    });
    stockBody.innerHTML = sHtml || `<tr><td colspan="5" class="text-center">No backtest breakdown available.</td></tr>`;

    // Trade execution logs
    const tradesBody = document.getElementById("bt-trades-table-body");
    let tHtml = "";
    (data.recent_trades || []).slice(-15).reverse().forEach(t => {
      const isProfit = t.Return_Pct > 0;
      tHtml += `
        <tr>
          <td class="font-mono font-bold">${t.Ticker}</td>
          <td class="font-mono">${t.Entry_Date}</td>
          <td class="font-mono">${t.Exit_Date}</td>
          <td class="font-mono">MYR ${t.Entry_Price}</td>
          <td class="font-mono">MYR ${t.Exit_Price}</td>
          <td class="font-mono ${isProfit ? 'text-green' : 'text-red'}">${isProfit ? '+' : ''}${t.Return_Pct}%</td>
          <td><span class="badge ${isProfit ? 'badge-buy' : 'badge-avoid'}">${t.Exit_Reason}</span></td>
        </tr>
      `;
    });
    tradesBody.innerHTML = tHtml || `<tr><td colspan="7" class="text-center">No trades logged.</td></tr>`;

  } catch (err) {
    clearInterval(btProgressInterval);
    document.getElementById("progress-card").classList.add("hidden");
    console.error("Backtest simulation error", err);
    btReturn.innerText = "Error";
  }
}
