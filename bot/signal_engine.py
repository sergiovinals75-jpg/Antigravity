"""
Motor de señales: combina RSI + Sentimiento fundamental.

Solo genera señal cuando AMBOS indicadores coinciden:
  - LARGO: RSI en sobreventa (<30) + sentimiento alcista (>+30)
  - CORTO: RSI en sobrecompra (>70) + sentimiento bajista (<-30)
"""
import logging

from bot.config import (
    RSI_OVERBOUGHT,
    RSI_OVERSOLD,
    SENTIMENT_BULLISH_THRESHOLD,
    SENTIMENT_BEARISH_THRESHOLD,
)

logger = logging.getLogger(__name__)

# Niveles de confianza
CONFIDENCE_LEVELS = {
    "ALTA":   "🟢🟢🟢",
    "MEDIA":  "🟡🟡",
    "BAJA":   "🔴",
}


def generate_signal(
    symbol: str,
    rsi_data: dict,
    sentiment_data: dict,
) -> dict:
    """
    Genera señal de trading basada en confluencia RSI + Sentimiento.

    Retorna:
        {
            "symbol": str,
            "signal": "LARGO" | "CORTO" | "SIN SEÑAL",
            "confidence": "ALTA" | "MEDIA" | "BAJA",
            "rsi": float,
            "rsi_zone": str,
            "sentiment_score": int,
            "sentiment_label": str,
            "reasoning": str,
            "current_price": float,
            "change_24h": float,
        }
    """
    rsi = rsi_data.get("rsi")
    rsi_zone = rsi_data.get("rsi_zone", "SIN DATOS")
    sentiment_score = sentiment_data.get("score", 0)
    sentiment_label = sentiment_data.get("label", "NEUTRAL")
    current_price = rsi_data.get("current_price")
    change_24h = rsi_data.get("change_24h")

    signal = "SIN SEÑAL"
    confidence = "BAJA"
    reasoning = ""

    # ── Sin datos de RSI ──
    if rsi is None:
        reasoning = "⚠️ No hay datos suficientes de RSI para este par."
        return _build_result(
            symbol, signal, confidence, rsi, rsi_zone,
            sentiment_score, sentiment_label, reasoning,
            current_price, change_24h
        )

    # ── SEÑAL LARGO ──
    # RSI en sobreventa + noticias alcistas
    if rsi <= RSI_OVERSOLD and sentiment_score >= SENTIMENT_BULLISH_THRESHOLD:
        signal = "LARGO"
        confidence = _calculate_confidence(rsi, sentiment_score, "LARGO")
        reasoning = (
            f"✅ CONFLUENCIA ALCISTA:\n"
            f"   • RSI({rsi}) en zona de SOBREVENTA (< {RSI_OVERSOLD})\n"
            f"   • Sentimiento fundamental ALCISTA ({sentiment_score:+d})\n"
            f"   • Las noticias respaldan una recuperación del precio"
        )

    # ── SEÑAL CORTO ──
    # RSI en sobrecompra + noticias bajistas
    elif rsi >= RSI_OVERBOUGHT and sentiment_score <= SENTIMENT_BEARISH_THRESHOLD:
        signal = "CORTO"
        confidence = _calculate_confidence(rsi, sentiment_score, "CORTO")
        reasoning = (
            f"✅ CONFLUENCIA BAJISTA:\n"
            f"   • RSI({rsi}) en zona de SOBRECOMPRA (> {RSI_OVERBOUGHT})\n"
            f"   • Sentimiento fundamental BAJISTA ({sentiment_score:+d})\n"
            f"   • Las noticias sugieren presión de venta"
        )

    # ── RSI extremo pero sentimiento contrario ──
    elif rsi <= RSI_OVERSOLD and sentiment_score <= SENTIMENT_BEARISH_THRESHOLD:
        reasoning = (
            f"⚠️ RSI en sobreventa ({rsi}) pero sentimiento bajista ({sentiment_score:+d}).\n"
            f"   Posible caída continuada — NO operar."
        )

    elif rsi >= RSI_OVERBOUGHT and sentiment_score >= SENTIMENT_BULLISH_THRESHOLD:
        reasoning = (
            f"⚠️ RSI en sobrecompra ({rsi}) pero sentimiento alcista ({sentiment_score:+d}).\n"
            f"   Posible rally continuado — NO operar contra tendencia."
        )

    # ── RSI en zona neutral ──
    elif RSI_OVERSOLD < rsi < RSI_OVERBOUGHT:
        reasoning = (
            f"RSI en zona neutral ({rsi}). "
            f"Sentimiento: {sentiment_label} ({sentiment_score:+d}).\n"
            f"   Sin confluencia técnica + fundamental."
        )

    else:
        reasoning = "Sin confluencia clara entre RSI y sentimiento."

    return _build_result(
        symbol, signal, confidence, rsi, rsi_zone,
        sentiment_score, sentiment_label, reasoning,
        current_price, change_24h
    )


def _calculate_confidence(rsi: float, sentiment_score: int, direction: str) -> str:
    """Calcula nivel de confianza basado en la fuerza de la confluencia."""
    if direction == "LARGO":
        rsi_strength = max(0, (RSI_OVERSOLD - rsi) / RSI_OVERSOLD)
        sent_strength = min(1, sentiment_score / 80)
    else:  # CORTO
        rsi_strength = max(0, (rsi - RSI_OVERBOUGHT) / (100 - RSI_OVERBOUGHT))
        sent_strength = min(1, abs(sentiment_score) / 80)

    combined = (rsi_strength + sent_strength) / 2

    if combined >= 0.6:
        return "ALTA"
    elif combined >= 0.3:
        return "MEDIA"
    else:
        return "BAJA"


def _build_result(
    symbol, signal, confidence, rsi, rsi_zone,
    sentiment_score, sentiment_label, reasoning,
    current_price, change_24h
) -> dict:
    return {
        "symbol": symbol,
        "signal": signal,
        "confidence": confidence,
        "confidence_emoji": CONFIDENCE_LEVELS.get(confidence, ""),
        "rsi": rsi,
        "rsi_zone": rsi_zone,
        "sentiment_score": sentiment_score,
        "sentiment_label": sentiment_label,
        "reasoning": reasoning,
        "current_price": current_price,
        "change_24h": change_24h,
    }
