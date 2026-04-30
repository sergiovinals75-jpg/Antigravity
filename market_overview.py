"""
Resumen del mercado crypto global.
Incluye: Fear & Greed Index, capitalización total, dominancia BTC.
"""
import logging
import requests

from bot.config import FEAR_GREED_URL, COINGECKO_BASE_URL

logger = logging.getLogger(__name__)


def get_fear_greed_index() -> dict:
    """
    Obtiene el índice Fear & Greed de Alternative.me.
    Retorna: {"value": int, "label": str, "timestamp": str}
    """
    try:
        resp = requests.get(FEAR_GREED_URL, timeout=15)
        resp.raise_for_status()
        data = resp.json().get("data", [{}])[0]
        value = int(data.get("value", 50))

        # Etiqueta en español
        if value <= 20:
            label = "Miedo Extremo 😱"
        elif value <= 40:
            label = "Miedo 😰"
        elif value <= 60:
            label = "Neutral 😐"
        elif value <= 80:
            label = "Codicia 🤑"
        else:
            label = "Codicia Extrema 🤩"

        return {"value": value, "label": label}

    except Exception as e:
        logger.error(f"Error Fear & Greed Index: {e}")
        return {"value": None, "label": "No disponible"}


def get_global_market_data() -> dict:
    """
    Datos globales del mercado desde CoinGecko.
    """
    try:
        resp = requests.get(
            f"{COINGECKO_BASE_URL}/global", timeout=15
        )
        resp.raise_for_status()
        data = resp.json().get("data", {})

        total_market_cap = data.get("total_market_cap", {}).get("usd", 0)
        total_volume = data.get("total_volume", {}).get("usd", 0)
        btc_dominance = data.get("market_cap_percentage", {}).get("btc", 0)
        eth_dominance = data.get("market_cap_percentage", {}).get("eth", 0)
        market_cap_change = data.get("market_cap_change_percentage_24h_usd", 0)

        return {
            "total_market_cap": total_market_cap,
            "total_volume": total_volume,
            "btc_dominance": round(btc_dominance, 1),
            "eth_dominance": round(eth_dominance, 1),
            "market_cap_change_24h": round(market_cap_change, 2),
        }

    except Exception as e:
        logger.error(f"Error datos globales: {e}")
        return {
            "total_market_cap": None,
            "total_volume": None,
            "btc_dominance": None,
            "eth_dominance": None,
            "market_cap_change_24h": None,
        }


def get_market_overview() -> dict:
    """Combina Fear & Greed + datos globales en un resumen."""
    fear_greed = get_fear_greed_index()
    global_data = get_global_market_data()

    return {
        "fear_greed": fear_greed,
        **global_data,
    }


def format_market_cap(value: float | None) -> str:
    """Formatea capitalización en billones/millones."""
    if value is None:
        return "N/A"
    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    elif value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    else:
        return f"${value:,.0f}"
