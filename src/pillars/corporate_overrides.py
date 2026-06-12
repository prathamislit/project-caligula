"""Static financial overlays for general corporate tickers.
Provides a defensive fallback to circumvent Yahoo Finance blocks in server environments.
"""

CORPORATE_OVERRIDES = {
    "AAPL": {
        "shortName": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics",
        "grossMargins": 0.45, "operatingMargins": 0.30, "returnOnAssets": 0.21, "returnOnEquity": 1.45,
        "freeCashflow": 110_000_000_000, "marketCap": 3_200_000_000_000, "totalDebt": 105_000_000_000,
        "ebitda": 130_000_000_000, "currentRatio": 1.15, "quickRatio": 0.95, "totalCash": 73_000_000_000,
        "revenueGrowth": 0.08, "earningsGrowth": 0.12, "pegRatio": 2.2, "shortPercentOfFloat": 0.012,
        "shortRatio": 1.8, "beta": 1.12
    },
    "NVDA": {
        "shortName": "NVIDIA Corporation", "sector": "Technology", "industry": "Semiconductors",
        "grossMargins": 0.76, "operatingMargins": 0.54, "returnOnAssets": 0.42, "returnOnEquity": 1.15,
        "freeCashflow": 46_000_000_000, "marketCap": 2_800_000_000_000, "totalDebt": 9_700_000_000,
        "ebitda": 62_000_000_000, "currentRatio": 3.8, "quickRatio": 3.2, "totalCash": 26_000_000_000,
        "revenueGrowth": 1.15, "earningsGrowth": 2.20, "pegRatio": 1.1, "shortPercentOfFloat": 0.015,
        "shortRatio": 1.4, "beta": 1.85
    },
    "MSFT": {
        "shortName": "Microsoft Corporation", "sector": "Technology", "industry": "Software—Infrastructure",
        "grossMargins": 0.70, "operatingMargins": 0.44, "returnOnAssets": 0.19, "returnOnEquity": 0.38,
        "freeCashflow": 70_000_000_000, "marketCap": 3_100_000_000_000, "totalDebt": 100_000_000_000,
        "ebitda": 102_000_000_000, "currentRatio": 1.22, "quickRatio": 1.05, "totalCash": 80_000_000_000,
        "revenueGrowth": 0.15, "earningsGrowth": 0.20, "pegRatio": 2.1, "shortPercentOfFloat": 0.008,
        "shortRatio": 1.6, "beta": 0.90
    },
    "TSLA": {
        "shortName": "Tesla, Inc.", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers",
        "grossMargins": 0.18, "operatingMargins": 0.08, "returnOnAssets": 0.07, "returnOnEquity": 0.14,
        "freeCashflow": 4_500_000_000, "marketCap": 650_000_000_000, "totalDebt": 9_500_000_000,
        "ebitda": 12_500_000_000, "currentRatio": 1.70, "quickRatio": 1.25, "totalCash": 27_000_000_000,
        "revenueGrowth": 0.05, "earningsGrowth": -0.08, "pegRatio": 4.2, "shortPercentOfFloat": 0.035,
        "shortRatio": 2.1, "beta": 2.30
    },
    "AMD": {
        "shortName": "Advanced Micro Devices, Inc.", "sector": "Technology", "industry": "Semiconductors",
        "grossMargins": 0.48, "operatingMargins": 0.11, "returnOnAssets": 0.04, "returnOnEquity": 0.05,
        "freeCashflow": 3_200_000_000, "marketCap": 240_000_000_000, "totalDebt": 3_000_000_000,
        "ebitda": 4_100_000_000, "currentRatio": 2.4, "quickRatio": 1.9, "totalCash": 5_800_000_000,
        "revenueGrowth": 0.12, "earningsGrowth": 0.18, "pegRatio": 1.8, "shortPercentOfFloat": 0.022,
        "shortRatio": 1.9, "beta": 1.68
    },
    "AMZN": {
        "shortName": "Amazon.com, Inc.", "sector": "Consumer Cyclical", "industry": "Internet Retail",
        "grossMargins": 0.47, "operatingMargins": 0.09, "returnOnAssets": 0.06, "returnOnEquity": 0.20,
        "freeCashflow": 32_000_000_000, "marketCap": 1_850_000_000_000, "totalDebt": 130_000_000_000,
        "ebitda": 85_000_000_000, "currentRatio": 1.05, "quickRatio": 0.85, "totalCash": 86_000_000_000,
        "revenueGrowth": 0.13, "earningsGrowth": 0.48, "pegRatio": 1.5, "shortPercentOfFloat": 0.011,
        "shortRatio": 1.7, "beta": 1.15
    },
    "META": {
        "shortName": "Meta Platforms, Inc.", "sector": "Communication Services", "industry": "Internet Content & Information",
        "grossMargins": 0.81, "operatingMargins": 0.38, "returnOnAssets": 0.17, "returnOnEquity": 0.28,
        "freeCashflow": 43_000_000_000, "marketCap": 1_200_000_000_000, "totalDebt": 18_000_000_000,
        "ebitda": 51_000_000_000, "currentRatio": 2.1, "quickRatio": 1.9, "totalCash": 65_000_000_000,
        "revenueGrowth": 0.22, "earningsGrowth": 0.35, "pegRatio": 1.2, "shortPercentOfFloat": 0.012,
        "shortRatio": 1.5, "beta": 1.20
    },
    "GOOGL": {
        "shortName": "Alphabet Inc.", "sector": "Communication Services", "industry": "Internet Content & Information",
        "grossMargins": 0.57, "operatingMargins": 0.28, "returnOnAssets": 0.14, "returnOnEquity": 0.24,
        "freeCashflow": 69_000_000_000, "marketCap": 2_100_000_000_000, "totalDebt": 28_000_000_000,
        "ebitda": 95_000_000_000, "currentRatio": 2.0, "quickRatio": 1.8, "totalCash": 110_000_000_000,
        "revenueGrowth": 0.14, "earningsGrowth": 0.19, "pegRatio": 1.4, "shortPercentOfFloat": 0.007,
        "shortRatio": 1.3, "beta": 1.05
    }
}
