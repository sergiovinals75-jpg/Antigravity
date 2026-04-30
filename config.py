"""
Configuración central del bot de señales crypto.
Todas las APIs utilizadas son 100% GRATUITAS — sin API keys necesarias.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
# Telegram
# ──────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ──────────────────────────────────────────────
# APIs (todas gratuitas, sin key)
# ──────────────────────────────────────────────
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
CRYPTOCOMPARE_NEWS_URL = "https://min-api.cryptocompare.com/data/v2/news/"
FEAR_GREED_URL = "https://api.alternative.me/fng/"

# ──────────────────────────────────────────────
# RSI
# ──────────────────────────────────────────────
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
PRICE_HISTORY_DAYS = 30

# ──────────────────────────────────────────────
# Sentimiento
# ──────────────────────────────────────────────
SENTIMENT_BULLISH_THRESHOLD = 30    # Score > 30 → alcista
SENTIMENT_BEARISH_THRESHOLD = -30   # Score < -30 → bajista

# ──────────────────────────────────────────────
# Monedas a rastrear  (símbolo → CoinGecko ID)
# ──────────────────────────────────────────────
TRACKED_COINS = {
    "BTC":   {"id": "bitcoin",        "name": "Bitcoin"},
    "ETH":   {"id": "ethereum",       "name": "Ethereum"},
    "BNB":   {"id": "binancecoin",    "name": "BNB"},
    "SOL":   {"id": "solana",         "name": "Solana"},
    "XRP":   {"id": "ripple",         "name": "XRP"},
    "ADA":   {"id": "cardano",        "name": "Cardano"},
    "DOGE":  {"id": "dogecoin",       "name": "Dogecoin"},
    "AVAX":  {"id": "avalanche-2",    "name": "Avalanche"},
    "DOT":   {"id": "polkadot",       "name": "Polkadot"},
    "LINK":  {"id": "chainlink",      "name": "Chainlink"},
    "MATIC": {"id": "matic-network",  "name": "Polygon"},
    "UNI":   {"id": "uniswap",        "name": "Uniswap"},
    "ATOM":  {"id": "cosmos",         "name": "Cosmos"},
    "NEAR":  {"id": "near",           "name": "NEAR Protocol"},
    "APT":   {"id": "aptos",          "name": "Aptos"},
    "ARB":   {"id": "arbitrum",       "name": "Arbitrum"},
    "SUI":   {"id": "sui",            "name": "Sui"},
}

# ──────────────────────────────────────────────
# CryptoCompare: mapeo de símbolo a categoría
# (CryptoCompare usa categorías para filtrar noticias)
# ──────────────────────────────────────────────
CRYPTOCOMPARE_CATEGORIES = {
    "BTC": "BTC", "ETH": "ETH", "BNB": "BNB", "SOL": "SOL",
    "XRP": "XRP", "ADA": "ADA", "DOGE": "DOGE", "AVAX": "AVAX",
    "DOT": "DOT", "LINK": "LINK", "MATIC": "MATIC", "UNI": "UNI",
    "ATOM": "ATOM", "NEAR": "NEAR", "APT": "APT", "ARB": "ARB",
    "SUI": "SUI",
}

# ──────────────────────────────────────────────
# Fuentes RSS de noticias crypto
# ──────────────────────────────────────────────
RSS_FEEDS = [
    "https://cointelegraph.com/rss",
    "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "https://decrypt.co/feed",
    "https://bitcoinmagazine.com/.rss/full/",
    "https://thedefiant.io/feed",
]

# ──────────────────────────────────────────────
# Google News RSS (búsqueda gratuita de noticias)
# ──────────────────────────────────────────────
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}+crypto&hl=en&gl=US&ceid=US:en"

# ──────────────────────────────────────────────
# Rate-limit entre llamadas API (segundos)
# ──────────────────────────────────────────────
API_DELAY = 1.5
