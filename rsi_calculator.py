"""
Calculador de RSI (Relative Strength Index) con método de Wilder.
Usa precios diarios de CoinGecko (API gratuita).
"""
import time
import logging
import requests
import numpy as np

from bot.config import (
    COINGECKO_BASE_URL,
    PRICE_HISTORY_DAYS,
    RSI_PERIOD,
    API_DELAY,
)

logger = logging.getLogger(__name__)


def fetch_daily_prices(coin_id: str, days: int = PRICE_HISTORY_DAYS) -> list[float]:
    """
    Obtiene precios de cierre diarios desde CoinGecko.
    Retorna lista de precios [más antiguo … más reciente].
    """
    url = f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily",
    }

    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        prices = [point[1] for point in data.get("prices", [])]
        logger.info(f"Precios obtenidos para {coin_id}: {len(prices)} días")
        return prices
    except Exception as e:
        logger.error(f"Error precios {coin_id}: {e}")
        return []


def calculate_rsi(prices: list[float], period: int = RSI_PERIOD) -> float | None:
    """
    Calcula el RSI con el método de suavizado de Wilder.
    Retorna valor entre 0 y 100, o None si no hay datos suficientes.
    """
    if len(prices) < period + 1:
        logger.warning(f"Datos insuficientes para RSI: {len(prices)} precios")
        return None

    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)

    # Primera media: promedio simple del primer período
    avg_gain = float(np.mean(gains[:period]))
    avg_loss = float(np.mean(losses[:period]))

    # Suavizado de Wilder para el resto
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))

    return round(rsi, 2)


def get_current_price(coin_id: str) -> dict | None:
    """Obtiene precio actual y cambio 24h desde CoinGecko."""
    url = f"{COINGECKO_BASE_URL}/simple/price"
    params = {
        "ids": coin_id,
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_market_cap": "true",
    }
    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json().get(coin_id, {})
        return {
            "price": data.get("usd", 0),
            "change_24h": round(data.get("usd_24h_change", 0), 2),
            "market_cap": data.get("usd_market_cap", 0),
        }
    except Exception as e:
        logger.error(f"Error precio actual {coin_id}: {e}")
        return None


def get_rsi_analysis(coin_id: str) -> dict:
    """
    Análisis técnico completo: RSI + precio actual + cambio 24h.
    """
    # Precio actual
    price_data = get_current_price(coin_id)
    time.sleep(API_DELAY)

    # Precios históricos para RSI
    prices = fetch_daily_prices(coin_id)
    time.sleep(API_DELAY)

    rsi = calculate_rsi(prices) if prices else None

    # Interpretar RSI
    if rsi is not None:
        if rsi >= 70:
            rsi_zone = "SOBRECOMPRA"
        elif rsi <= 30:
            rsi_zone = "SOBREVENTA"
        else:
            rsi_zone = "NEUTRAL"
    else:
        rsi_zone = "SIN DATOS"

    return {
        "rsi": rsi,
        "rsi_zone": rsi_zone,
        "current_price": price_data["price"] if price_data else None,
        "change_24h": price_data["change_24h"] if price_data else None,
        "market_cap": price_data["market_cap"] if price_data else None,
    }
