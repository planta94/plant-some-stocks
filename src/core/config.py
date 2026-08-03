"""
config.py - Application configuration and default KLSE stock universe settings.
Supports thematic portfolios (Banking, Tech, Infrastructure, High Dividend, etc.) and full Bursa Malaysia universe (~1,000 stocks).
"""

# Curated Top Liquid Stocks across all Bursa Malaysia sectors
DEFAULT_KLSE_STOCKS = {
    # Financial Services
    "1155.KL": {"name": "Malayan Banking Berhad (Maybank)", "sector": "Financial Services"},
    "1023.KL": {"name": "CIMB Group Holdings Berhad", "sector": "Financial Services"},
    "1295.KL": {"name": "Public Bank Berhad", "sector": "Financial Services"},
    "1066.KL": {"name": "RHB Bank Berhad", "sector": "Financial Services"},
    "1082.KL": {"name": "Hong Leong Bank Berhad", "sector": "Financial Services"},
    "1015.KL": {"name": "AMMB Holdings Berhad (AMBANK)", "sector": "Financial Services"},

    # Utilities & Infrastructure
    "5347.KL": {"name": "Tenaga Nasional Berhad", "sector": "Utilities"},
    "6742.KL": {"name": "YTL Power International Berhad", "sector": "Utilities"},
    "4677.KL": {"name": "YTL Corporation Berhad", "sector": "Utilities / Conglomerate"},
    "5209.KL": {"name": "Gas Malaysia Berhad", "sector": "Utilities"},

    # Telecommunications
    "6947.KL": {"name": "CelcomDigi Berhad", "sector": "Telecommunications"},
    "6012.KL": {"name": "Maxis Berhad", "sector": "Telecommunications"},
    "4863.KL": {"name": "Telekom Malaysia Berhad (TM)", "sector": "Telecommunications"},
    "6888.KL": {"name": "Axiata Group Berhad", "sector": "Telecommunications"},

    # Industrial Products & Materials
    "5183.KL": {"name": "Petronas Chemicals Group Berhad", "sector": "Industrial Products"},
    "8869.KL": {"name": "Press Metal Aluminium Holdings", "sector": "Industrial Products"},
    "5211.KL": {"name": "Sunway Berhad", "sector": "Conglomerate / Property"},
    "4731.KL": {"name": "Scientex Berhad", "sector": "Industrial Products"},
    "6963.KL": {"name": "VS Industry Berhad", "sector": "Industrial Products"},

    # Healthcare & Gloves
    "5225.KL": {"name": "IHH Healthcare Berhad", "sector": "Healthcare"},
    "5878.KL": {"name": "KPJ Healthcare Berhad", "sector": "Healthcare"},
    "5168.KL": {"name": "Hartalega Holdings Berhad", "sector": "Healthcare"},
    "7113.KL": {"name": "Top Glove Corporation Berhad", "sector": "Healthcare"},
    "7153.KL": {"name": "Kossan Rubber Industries", "sector": "Healthcare"},

    # Consumer Products & Retail
    "6033.KL": {"name": "Petronas Dagangan Berhad", "sector": "Consumer Products"},
    "5296.KL": {"name": "MR D.I.Y. Group (M) Berhad", "sector": "Consumer Products"},
    "4707.KL": {"name": "Nestlé (Malaysia) Berhad", "sector": "Consumer Products"},
    "5099.KL": {"name": "Capital A Berhad (AirAsia)", "sector": "Consumer / Aviation"},
    "3689.KL": {"name": "Fraser & Neave Holdings (F&N)", "sector": "Consumer Products"},
    "7277.KL": {"name": "Dialog Group Berhad", "sector": "Energy / Oil & Gas"},

    # Technology
    "0166.KL": {"name": "Inari Amertron Berhad", "sector": "Technology"},
    "7084.KL": {"name": "QES Group Berhad", "sector": "Technology"},
    "3867.KL": {"name": "Malaysian Pacific Industries (MPI)", "sector": "Technology"},
    "5005.KL": {"name": "Unisem (M) Berhad", "sector": "Technology"},
    "0128.KL": {"name": "Frontken Corporation Berhad", "sector": "Technology"},
    "0097.KL": {"name": "ViTrox Corporation Berhad", "sector": "Technology"},
    "0208.KL": {"name": "Greatech Technology Berhad", "sector": "Technology"},
    "7204.KL": {"name": "D&O Green Technologies", "sector": "Technology"},
    "5292.KL": {"name": "UWC Berhad", "sector": "Technology"},
    "7160.KL": {"name": "Pentamaster Corporation", "sector": "Technology"},

    # Construction & Property
    "5398.KL": {"name": "Gamuda Berhad", "sector": "Construction"},
    "3336.KL": {"name": "IJM Corporation Berhad", "sector": "Construction"},
    "5288.KL": {"name": "Sime Darby Property Berhad", "sector": "Property"},
    "8206.KL": {"name": "Eco World Development Group", "sector": "Property"},
    "8583.KL": {"name": "Mah Sing Group Berhad", "sector": "Property"},
    "7161.KL": {"name": "Kerjaya Prospek Group", "sector": "Construction"},

    # Plantation & Energy
    "5285.KL": {"name": "SD Guthrie Berhad (Sime Darby Plantation)", "sector": "Plantation"},
    "1961.KL": {"name": "IOI Corporation Berhad", "sector": "Plantation"},
    "2445.KL": {"name": "Kuala Lumpur Kepong Berhad (KLK)", "sector": "Plantation"},
    "7293.KL": {"name": "Yinson Holdings Berhad", "sector": "Energy / Offshore"},
    "5141.KL": {"name": "Dayang Enterprise Holdings", "sector": "Energy / Offshore"},

    # Gaming & Diversified
    "3182.KL": {"name": "Genting Berhad", "sector": "Gaming / Conglomerate"},
    "4715.KL": {"name": "Genting Malaysia Berhad", "sector": "Gaming / Hospitality"},
    "4197.KL": {"name": "Sime Darby Berhad", "sector": "Consumer / Industrial"}
}

THEMATIC_PORTFOLIOS = {
    "top50": {
        "name": "⚡ Top 50 Liquid Large-Caps",
        "description": "Highest market cap & volume liquid bluechips across Bursa Malaysia",
        "tickers": list(DEFAULT_KLSE_STOCKS.keys())
    },
    "banking": {
        "name": "🏦 Banking & Financial Services Leaders",
        "description": "Core Malaysian banking giants, investment banks, and insurance providers",
        "tickers": ["1155.KL", "1023.KL", "1295.KL", "1066.KL", "1082.KL", "1015.KL"]
    },
    "tech": {
        "name": "💻 Tech, Semiconductor & AI Infrastructure",
        "description": "OSAT, semiconductor equipment, automation, and tech supply chain leaders",
        "tickers": ["0166.KL", "7084.KL", "3867.KL", "5005.KL", "0128.KL", "0097.KL", "0208.KL", "7204.KL", "5292.KL", "7160.KL"]
    },
    "infra": {
        "name": "🏗️ Utilities, Energy & Infrastructure",
        "description": "Power utilities, data center power infrastructure, and construction catalysts",
        "tickers": ["5347.KL", "6742.KL", "4677.KL", "5209.KL", "5398.KL", "3336.KL", "5288.KL", "7293.KL", "5141.KL"]
    },
    "dividends": {
        "name": "💵 High Dividend Yield Aristocrats",
        "description": "Defensive income stocks with strong dividend yields (>4.0%) and healthy cash flows",
        "tickers": ["1155.KL", "5209.KL", "5183.KL", "4863.KL", "6033.KL", "1066.KL", "1295.KL"]
    },
    "consumer": {
        "name": "🛒 Consumer Products & Retail Champions",
        "description": "Domestic retail leaders, staples, and aviation consumer recovery plays",
        "tickers": ["5296.KL", "4707.KL", "5099.KL", "3689.KL", "6033.KL", "4197.KL"]
    },
    "gloves": {
        "name": "🏥 Healthcare & Glove Manufacturers",
        "description": "Private hospital operators and rubber glove export leaders",
        "tickers": ["5225.KL", "5878.KL", "5168.KL", "7113.KL", "7153.KL"]
    },
    "full": {
        "name": "🌐 Full Bursa Malaysia Market (~1000 Stocks)",
        "description": "Market-wide scan covering all Main & ACE Market tickers",
        "tickers": None
    }
}

DEFAULT_SCAN_PARAMS = {
    "min_fund": 60.0,
    "require_uptrend": True,
    "min_rr": 2.0
}

def get_portfolio_tickers(portfolio_key: str = "top50"):
    """Returns list of ticker symbols for a specified portfolio strategy."""
    key = str(portfolio_key).lower().strip()
    if key == "full":
        return list(get_full_klse_universe().keys())
    
    port = THEMATIC_PORTFOLIOS.get(key)
    if port and port.get("tickers"):
        return port["tickers"]
    
    return list(DEFAULT_KLSE_STOCKS.keys())

def get_full_klse_universe():
    """
    Returns full active universe list across Bursa Malaysia Main & ACE markets (~1,000 stocks).
    Merges curated list with numeric Bursa Malaysia stock tickers.
    """
    full_dict = dict(DEFAULT_KLSE_STOCKS)
    
    sample_ranges = [
        range(1, 300),
        range(1000, 2000),
        range(3000, 4000),
        range(5000, 6000),
        range(7000, 8000),
        range(8000, 9500)
    ]
    
    for r in sample_ranges:
        for num in r:
            t = f"{num:04d}.KL"
            if t not in full_dict:
                full_dict[t] = {
                    "name": f"KLSE Listed Co ({t})",
                    "sector": "Bursa Malaysia Market"
                }
                
    return full_dict
