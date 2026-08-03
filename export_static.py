"""
export_static.py - Generates static dashboard build in dist/ for GitHub Pages or Google Pages.
Executes live scan across stock universe and bakes scan results directly into index.html.
"""

import os
import json
import shutil
import sys

# Ensure UTF-8 output encoding for console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from src.engines.live_engine import run_live_scan, analyze_stock
from src.data.fetcher import fetch_klse_stock_data
from src.core.config import DEFAULT_KLSE_STOCKS

def generate_static_site():
    print("[INFO] Building static deployment bundle for GitHub Pages / Google Pages...")

    # 1. Ensure dist/ output directory exists
    dist_dir = os.path.join(os.path.dirname(__file__), "dist")
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)

    # 2. Run live scan to build pre-rendered dataset
    print("[INFO] Pre-computing quantitative scan for KLSE stock universe...")
    scan_data = run_live_scan(min_fund=40.0, require_uptrend=False, min_rr=1.5)
    
    # Attach chart data for top stocks
    for item in scan_data["results"]:
        df, fun = fetch_klse_stock_data(item["ticker"])
        bp = analyze_stock(df, fun)
        item["chart_data"] = bp.get("chart_data", [])
        item["metrics"] = bp.get("metrics", {})
        item["entry_range"] = bp.get("entry_range", "")

    # 3. Copy modular static CSS & JS directories
    static_dir = os.path.join(os.path.dirname(__file__), "src", "static")
    shutil.copytree(os.path.join(static_dir, "css"), os.path.join(dist_dir, "css"))
    shutil.copytree(os.path.join(static_dir, "js"), os.path.join(dist_dir, "js"))

    # 4. Read HTML template & inject window.STATIC_SCAN_DATA
    with open(os.path.join(static_dir, "index.html"), "r", encoding="utf-8") as f:
        html_content = f.read()

    injection_script = f"""
    <script>
      window.STATIC_SCAN_DATA = {json.dumps(scan_data)};
    </script>
    """
    
    modified_html = html_content.replace("</head>", f"{injection_script}\n</head>")

    with open(os.path.join(dist_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(modified_html)

    print(f"[SUCCESS] Static build created successfully in: {dist_dir}")
    print("[INFO] Ready for deployment to GitHub Pages or Google Cloud Storage static web hosting!")

if __name__ == "__main__":
    generate_static_site()
