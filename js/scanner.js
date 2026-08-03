/* scanner.js - Live Stock Matrix, Progress Monitor & Filter Controls Module */

let scanDataCache = [];
let progressInterval = null;

function updateFilterLabel(param, val) {
  if (param === 'min-fund') {
    document.getElementById('val-min-fund').innerText = val;
  } else if (param === 'min-rr') {
    document.getElementById('val-min-rr').innerText = val;
  }
}

function showProgressMonitor(titleText, initialStatus) {
  const card = document.getElementById("progress-card");
  if (!card) return;
  card.classList.remove("hidden");
  document.getElementById("progress-title").innerHTML = `<i class="fa-solid fa-circle-notch fa-spin text-cyan"></i> ${titleText}`;
  updateProgressMonitor(5, initialStatus, "0 / --");
}

function updateProgressMonitor(percent, statusText, countText) {
  const fill = document.getElementById("progress-bar-fill");
  const percentText = document.getElementById("progress-percent");
  const statusLabel = document.getElementById("progress-status-text");
  const countLabel = document.getElementById("progress-count-text");

  if (fill) fill.style.width = `${percent}%`;
  if (percentText) percentText.innerText = `${Math.min(100, Math.round(percent))}%`;
  if (statusLabel) statusLabel.innerText = statusText;
  if (countLabel) countLabel.innerText = countText;
}

function completeProgressMonitor(completedStatus, totalCount) {
  clearInterval(progressInterval);
  updateProgressMonitor(100, completedStatus, `${totalCount} / ${totalCount}`);
  document.getElementById("progress-title").innerHTML = `<i class="fa-solid fa-circle-check text-green"></i> Scan Completed Successfully!`;
  setTimeout(() => {
    const card = document.getElementById("progress-card");
    if (card) card.classList.add("hidden");
  }, 2500);
}

async function runLiveScan() {
  const scope = document.getElementById("input-universe-scope") ? document.getElementById("input-universe-scope").value : "top50";
  const fullMarket = (scope === "full");
  const minFund = document.getElementById("input-min-fund").value;
  const minRR = document.getElementById("input-min-rr").value;
  const requireUptrend = document.getElementById("input-require-uptrend").checked;

  const summaryBadge = document.getElementById("scan-summary-badge");
  summaryBadge.className = "badge badge-info";
  summaryBadge.innerText = fullMarket ? "Scanning Entire Bursa Market..." : "Scanning Market Data...";

  const tbody = document.getElementById("matrix-table-body");
  tbody.innerHTML = `<tr><td colspan="11" class="text-center loading-cell"><i class="fa-solid fa-circle-notch fa-spin"></i> Fetching live quantitative signals...</td></tr>`;

  // Start Visual Progress Monitor Animation
  const totalApprox = fullMarket ? 1000 : 52;
  showProgressMonitor(fullMarket ? "Scanning Bursa Malaysia Universe..." : "Scanning Top Liquid Universe...", "Stage 1: Running Fast-Gatekeeper Filters...");

  let currProgress = 10;
  clearInterval(progressInterval);
  progressInterval = setInterval(() => {
    if (currProgress < 90) {
      currProgress += Math.random() * 8 + 3;
      const count = Math.min(totalApprox, Math.round((currProgress / 100) * totalApprox));
      const status = currProgress < 40 ? "Applying Stage 1 Early-Exit Filters..." : "Calculating EMA 200, RSI & Target Upsides...";
      updateProgressMonitor(currProgress, status, `${count} / ${totalApprox}`);
    }
  }, 250);

  try {
    const data = await API.scanLive(minFund, minRR, requireUptrend, fullMarket, scope);
    completeProgressMonitor(`Evaluated ${data.total_scanned} stocks. Matched ${data.matched_count} recommendations.`, data.total_scanned);
    renderMatrixTable(data);
  } catch (err) {
    clearInterval(progressInterval);
    document.getElementById("progress-card").classList.add("hidden");
    tbody.innerHTML = `<tr><td colspan="11" class="text-center text-red font-semibold"><i class="fa-solid fa-triangle-exclamation"></i> Live API Error: ${err.message}</td></tr>`;
    summaryBadge.className = "badge badge-avoid";
    summaryBadge.innerText = "API Error";
    console.error("Live Scan API Error:", err);
  }
}


function renderMatrixTable(data) {
  scanDataCache = data.results || [];
  const tbody = document.getElementById("matrix-table-body");
  const summaryBadge = document.getElementById("scan-summary-badge");

  summaryBadge.className = "badge badge-buy";
  summaryBadge.innerText = `${data.matched_count} / ${data.total_scanned} Qualified Stocks`;

  if (scanDataCache.length === 0) {
    tbody.innerHTML = `<tr><td colspan="11" class="text-center">No stocks matched your current criteria. Try lowering the thresholds.</td></tr>`;
    return;
  }

  let html = "";
  scanDataCache.forEach(item => {
    let badgeClass = "badge-hold";
    if (item.recommendation === "STRONG BUY") badgeClass = "badge-strong-buy";
    else if (item.recommendation === "BUY") badgeClass = "badge-buy";
    else if (item.recommendation === "AVOID / WATCH") badgeClass = "badge-avoid";

    html += `
      <tr>
        <td class="font-mono font-bold">${item.ticker}</td>
        <td>${item.symbol}</td>
        <td><span class="badge ${badgeClass}">${item.recommendation}</span></td>
        <td class="font-mono">MYR ${item.current_price.toFixed(2)}</td>
        <td class="font-mono text-cyan">MYR ${item.entry_price.toFixed(2)}</td>
        <td class="font-mono text-green">MYR ${item.target_price.toFixed(2)}</td>
        <td class="font-mono text-red">MYR ${item.stop_loss.toFixed(2)}</td>
        <td class="font-mono text-green">+${item.upside_pct}%</td>
        <td class="font-mono text-gold">${item.risk_reward_ratio}</td>
        <td class="font-mono font-bold">${item.quant_score}</td>
        <td>
          <button class="btn btn-primary btn-sm" onclick="inspectStock('${item.ticker}')">
            <i class="fa-solid fa-chart-line"></i> Inspect
          </button>
        </td>
      </tr>
    `;
  });
  tbody.innerHTML = html;

  // Auto inspect first stock
  if (scanDataCache.length > 0) {
    inspectStock(scanDataCache[0].ticker);
  }
}
