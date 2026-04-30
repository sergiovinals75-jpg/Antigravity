"""
Módulo de obtención de noticias crypto — 100% GRATUITO.

Fuentes (sin API keys):
  1. CryptoCompare News API (gratuita, sin key)
  2. Google News RSS (búsqueda libre)
  3. RSS directo: CoinDesk, CoinTelegraph, Decrypt, Bitcoin Magazine, The Defiant
  4. CoinGecko trending
"""
import time
import logging
import requests
import feedparser
from datetime import datetime, timedelta, timezone

from bot.config import (
    CRYPTOCOMPARE_NEWS_URL,
    CRYPTOCOMPARE_CATEGORIES,
    COINGECKO_BASE_URL,
    GOOGLE_NEWS_RSS,
    RSS_FEEDS,
)

logger = logging.getLogger(__name__)


# ─── CryptoCompare News (gratuita, sin key) ──────────────────
def fetch_cryptocompare_news(symbol: str, max_items: int = 20) -> list[dict]:
    """
    Obtiene noticias de CryptoCompare filtradas por moneda.
    API 100% gratuita, no requiere autenticación.
    Fuentes: CoinDesk, CoinTelegraph, The Block, Decrypt, etc.
    """
    category = CRYPTOCOMPARE_CATEGORIES.get(symbol, symbol)

    params = {
        "categories": category,
        "excludeCategories": "Sponsored",
        "extraParams": "CryptoSignalBot",
    }

    try:
        resp = requests.get(CRYPTOCOMPARE_NEWS_URL, params=params, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        results = []

        for article in data.get("Data", [])[:max_items]:
            # CryptoCompare no da sentimiento, se analizará por keywords
            published_ts = article.get("published_on", 0)
            published_dt = datetime.fromtimestamp(published_ts, tz=timezone.utc)

            # Solo noticias de las últimas 48h
            cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
            if published_dt < cutoff:
                continue

            results.append({
                "title": article.get("title", ""),
                "url": article.get("url", ""),
                "source": article.get("source_info", {}).get("name", article.get("source", "CryptoCompare")),
                "published_at": published_dt.isoformat(),
                "body": article.get("body", "")[:300],  # Primeros 300 chars del cuerpo
                "sentiment": "neutral",  # Se analizará después por keywords
            })

        logger.info(f"CryptoCompare: {len(results)} noticias para {symbol}")
        return results

    except Exception as e:
        logger.error(f"Error CryptoCompare ({symbol}): {e}")
        return []


# ─── Google News RSS (gratuito) ───────────────────────────────
def fetch_google_news(symbol: str, coin_name: str, max_items: int = 10) -> list[dict]:
    """
    Busca noticias en Google News RSS — completamente gratuito.
    """
    results = []
    queries = [f"{coin_name} crypto", f"{symbol} cryptocurrency"]

    for query in queries:
        url = GOOGLE_NEWS_RSS.format(query=query.replace(" ", "+"))

        try:
            feed = feedparser.parse(url)

            for entry in feed.entries[:max_items]:
                # Filtrar solo últimas 48h
                published = entry.get("published_parsed")
                if published:
                    pub_dt = datetime(*published[:6], tzinfo=timezone.utc)
                    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
                    if pub_dt < cutoff:
                        continue

                results.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "source": entry.get("source", {}).get("title", "Google News") if isinstance(entry.get("source"), dict) else "Google News",
                    "published_at": entry.get("published", ""),
                    "body": "",
                    "sentiment": "neutral",
                })

        except Exception as e:
            logger.warning(f"Error Google News ({query}): {e}")
            continue

    logger.info(f"Google News: {len(results)} noticias para {symbol}")
    return results


# ─── RSS Feeds directos ──────────────────────────────────────
def fetch_rss_news(symbol: str, coin_name: str, max_hours: int = 48) -> list[dict]:
    """
    Busca noticias en feeds RSS que mencionen el símbolo o nombre de la moneda.
    """
    results = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=max_hours)
    search_terms = [symbol.lower(), coin_name.lower()]

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            source = feed.feed.get("title", feed_url)

            for entry in feed.entries[:30]:
                title = entry.get("title", "").lower()
                summary = entry.get("summary", "").lower()
                content = title + " " + summary

                # Filtrar por relevancia a la moneda
                if not any(term in content for term in search_terms):
                    continue

                # Filtrar por fecha
                published = entry.get("published_parsed")
                if published:
                    pub_dt = datetime(*published[:6], tzinfo=timezone.utc)
                    if pub_dt < cutoff:
                        continue

                results.append({
                    "title": entry.get("title", ""),
                    "url": entry.get("link", ""),
                    "source": source,
                    "published_at": entry.get("published", ""),
                    "body": entry.get("summary", "")[:300],
                    "sentiment": "neutral",
                })

        except Exception as e:
            logger.warning(f"Error RSS ({feed_url}): {e}")
            continue

    logger.info(f"RSS: {len(results)} noticias para {symbol}")
    return results


# ─── CoinGecko trending ──────────────────────────────────────
def fetch_coingecko_trending() -> list[str]:
    """Devuelve los IDs de las monedas trending en CoinGecko."""
    try:
        resp = requests.get(
            f"{COINGECKO_BASE_URL}/search/trending", timeout=15
        )
        resp.raise_for_status()
        data = resp.json()
        trending = [
            coin["item"]["id"]
            for coin in data.get("coins", [])
        ]
        logger.info(f"CoinGecko trending: {trending}")
        return trending
    except Exception as e:
        logger.error(f"Error CoinGecko trending: {e}")
        return []


# ─── Función principal ───────────────────────────────────────
def get_all_news(symbol: str, coin_name: str) -> list[dict]:
    """
    Combina noticias de TODAS las fuentes gratuitas para una moneda.
    Elimina duplicados por título similar.
    """
    all_news = []

    # 1. CryptoCompare (fuente principal, gratuita)
    all_news.extend(fetch_cryptocompare_news(symbol))
    time.sleep(0.3)

    # 2. Google News RSS (búsqueda abierta)
    all_news.extend(fetch_google_news(symbol, coin_name))
    time.sleep(0.3)

    # 3. RSS feeds directos
    all_news.extend(fetch_rss_news(symbol, coin_name))

    # Eliminar duplicados por título (comparación aproximada)
    seen_titles = set()
    unique_news = []
    for item in all_news:
        # Normalizar título para detección de duplicados
        title_key = "".join(c for c in item["title"].lower()[:50] if c.isalnum())
        if title_key and title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_news.append(item)

    logger.info(
        f"Total noticias únicas para {symbol}: {len(unique_news)}"
    )
    return unique_news
