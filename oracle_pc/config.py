from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
LAKE_DIR = DATA_DIR / "lake"
MANUAL_DIR = DATA_DIR / "manual"
LOGS_DIR = BASE_DIR / "logs"
LEDGER_PATH = DATA_DIR / "predictions.jsonl"

MODEL_VERSION = "v0"

RUN_DATE_FMT = "%Y-%m-%d"

TF_BASE = "https://www.trendforce.com"
TF_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126 Safari/537.36"
    )
}
TF_PRICE_PAGES = {
    "dram_spot": {
        "url": f"{TF_BASE}/price/dram/dram_spot",
        "tokens": ["DDR5", "DDR4", "DDR3"],
        "cadence": "daily",
    },
    "nand_spot": {
        "url": f"{TF_BASE}/price/flash/flash_spot",
        "tokens": ["TLC"],
        "cadence": "daily",
    },
    "ssd_street": {
        "url": f"{TF_BASE}/price/flash/ssd_street",
        "tokens": [],
        "cadence": "biweekly",
    },
}
TF_PRESS_URL = f"{TF_BASE}/presscenter/news/"
PRESS_KEYWORDS = ("dram", "nand", "memory", "ssd", "flash", "hbm", "storage")

TICKER_BUCKETS = {
    "memory": ["MU", "SKHY", "SNDK", "WDC", "STX", "000660.KS", "005930.KS", "285A.T"],
    "demand": [
        "NVDA", "AMD", "INTC", "AAPL", "DELL", "HPQ", "0992.HK",
        "MSFT", "AMZN", "GOOGL", "META",
    ],
    "enablers": ["TSM", "ASML", "AMAT", "LRCX", "KLAC", "8035.T"],
    "benchmarks": ["^SOX", "^IXIC", "^KS11", "^TNX"],
}
ALL_TICKERS = [t for ts in TICKER_BUCKETS.values() for t in ts]

MEMORY_BASKET = ["MU", "SKHY", "SNDK", "WDC", "STX", "000660.KS"]
KOREA_MEMORY = ["005930.KS", "000660.KS"]

KOREA_MANUAL_CSV = MANUAL_DIR / "korea_semi_exports.csv"
KOREA_SCHEMA = {
    "period": "string",
    "window_type": "string",
    "exports_usd_mn": "float64",
    "yoy_pct": "float64",
}

SANITY_PCT_LIMIT = 35.0
MARKET_BACKFILL_DAYS = 750
