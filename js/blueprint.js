/* blueprint.js - Stock Blueprint Inspector & ApexCharts Module */

let currentChart = null;

async function inspectStock(ticker) {
  document.getElementById("blueprint-placeholder").classList.add("hidden");
  document.getElementById("blueprint-details").classList.remove("hidden");

  // Scroll to inspector on mobile
  if (window.innerWidth <= 1200) {
    document.getElementById("blueprint-panel").scrollIntoView({ behavior: 'smooth' });
  }

  try {
    const stock = await API.fetchStock(ticker);
    renderBlueprintDetails(stock);
  } catch (err) {
    console.warn("Could not fetch stock details from backend API", err);
    // Find in scan cache if offline
    const cached = scanDataCache.find(s => s.ticker === ticker);
    if (cached) renderBlueprintDetails(cached);
  }
}

function renderBlueprintDetails(stock) {
  document.getElementById("bp-name").innerText = stock.symbol || stock.name;
  document.getElementById("bp-ticker").innerText = stock.ticker;
  document.getElementById("bp-sector").innerText = stock.sector || "General";
  document.getElementById("bp-score").innerText = stock.quant_score;

  document.getElementById("bp-ep").innerText = `MYR ${stock.entry_price.toFixed(2)}`;
  document.getElementById("bp-ep-range").innerText = stock.entry_range || `MYR ${(stock.entry_price*0.995).toFixed(2)} - MYR ${stock.entry_price.toFixed(2)}`;
  
  document.getElementById("bp-tp").innerText = `MYR ${stock.target_price.toFixed(2)}`;
  document.getElementById("bp-upside").innerText = `+${stock.upside_pct}% Target Upside`;

  document.getElementById("bp-sl").innerText = `MYR ${stock.stop_loss.toFixed(2)}`;
  document.getElementById("bp-downside").innerText = `-${stock.downside_pct}% Downside Risk`;

  document.getElementById("bp-rr").innerText = stock.risk_reward_ratio;
  document.getElementById("bp-signal-text").innerText = stock.recommendation;
  document.getElementById("bp-action-note").innerHTML = `<i class="fa-solid fa-circle-info"></i> ${stock.action_note}`;

  // Reasoning Justification Breakdown Card
  if (stock.reasoning) {
    const fundUl = document.getElementById("bp-fund-reasons");
    const techUl = document.getElementById("bp-tech-reasons");
    const rrP = document.getElementById("bp-rr-reason");

    if (fundUl) {
      fundUl.innerHTML = (stock.reasoning.fundamental_reasons || [])
        .map(r => `<li><i class="fa-solid fa-check text-green"></i> ${r}</li>`)
        .join("") || "<li>Standard fundamental baseline met</li>";
    }

    if (techUl) {
      techUl.innerHTML = (stock.reasoning.technical_reasons || [])
        .map(r => `<li><i class="fa-solid fa-chart-simple text-cyan"></i> ${r}</li>`)
        .join("") || "<li>Standard technical alignment</li>";
    }

    if (rrP) {
      rrP.innerText = stock.reasoning.risk_reward_reason || "";
    }
  }

  // Metrics Grid
  const metricsGrid = document.getElementById("bp-metrics-grid");
  if (stock.metrics) {
    let mHtml = "";
    for (const [k, v] of Object.entries(stock.metrics)) {
      mHtml += `
        <div class="metric-item">
          <div class="metric-name">${k}</div>
          <div class="metric-val">${v}</div>
        </div>
      `;
    }
    metricsGrid.innerHTML = mHtml;
  }

  // Render ApexChart if chart data is present
  if (stock.chart_data && stock.chart_data.length > 0) {
    renderTechnicalChart(stock.chart_data);
  }
}

function renderTechnicalChart(seriesData) {
  const chartElement = document.querySelector("#stock-chart");
  chartElement.innerHTML = "";

  const candleData = seriesData.map(d => ({
    x: d.date,
    y: [d.open, d.high, d.low, d.close]
  }));

  const ema20 = seriesData.map(d => ({ x: d.date, y: d.ema20 }));
  const ema50 = seriesData.map(d => ({ x: d.date, y: d.ema50 }));
  const ema200 = seriesData.map(d => ({ x: d.date, y: d.ema200 }));

  const isMobile = window.innerWidth < 768;

  const options = {
    series: [
      { name: 'Candlestick', type: 'candlestick', data: candleData },
      { name: 'EMA 20', type: 'line', data: ema20 },
      { name: 'EMA 50', type: 'line', data: ema50 },
      { name: 'EMA 200', type: 'line', data: ema200 }
    ],
    chart: {
      type: 'candlestick',
      height: isMobile ? 260 : 320,
      background: 'transparent',
      toolbar: { show: false }
    },
    theme: { mode: 'dark' },
    colors: ['#00B5FF', '#F59E0B', '#3B82F6', '#8B5CF6'],
    stroke: { width: [1, 2, 2, 2] },
    xaxis: { type: 'category', labels: { style: { colors: '#94a3b8' } } },
    yaxis: { tooltip: { enabled: true }, labels: { style: { colors: '#94a3b8' } } },
    grid: { borderColor: 'rgba(255, 255, 255, 0.05)' }
  };

  if (currentChart) {
    currentChart.destroy();
  }
  currentChart = new ApexCharts(chartElement, options);
  currentChart.render();
}
