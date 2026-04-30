"""
Analizador de sentimiento de noticias crypto.

Método 100% local (sin APIs de pago):
  - Análisis por palabras clave ampliado (título + cuerpo)
  - Puntuación ponderada por fuente
  - Score final de -100 a +100
"""
import logging

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Diccionarios de palabras clave
# ──────────────────────────────────────────────
BULLISH_KEYWORDS = {
    # Inglés — alta señal
    "surge": 2, "rally": 2, "bullish": 2, "breakout": 2, "soar": 2,
    "all-time high": 3, "ath": 2, "moon": 1.5, "pump": 1.5,
    # Inglés — media señal
    "jump": 1.5, "gain": 1.5, "rise": 1.2, "climb": 1.2, "rebound": 1.5,
    "adoption": 1.5, "partnership": 1.5, "upgrade": 1.3, "launch": 1.2,
    "approval": 2, "approved": 2, "etf": 1.8, "institutional": 1.5,
    "accumulation": 1.5, "support": 1, "recovery": 1.5, "milestone": 1.3,
    "record": 1.3, "growth": 1.2, "positive": 1, "boost": 1.3,
    "integration": 1.2, "listing": 1.3, "invest": 1.2, "inflow": 1.5,
    "buy": 1, "whale": 1.2, "accumulate": 1.3, "unlock": 1,
    "mainstream": 1.2, "optimism": 1.3, "outperform": 1.5,
    "green": 1, "profit": 1.2, "demand": 1.3, "strong": 1,
    # Español
    "sube": 1.5, "subida": 1.5, "alcista": 2, "máximo": 1.5,
    "crecimiento": 1.2, "positivo": 1, "aprobación": 2,
    "lanzamiento": 1.2, "récord": 1.5, "impulso": 1.3,
    "inversión": 1.2, "adopción": 1.5, "alianza": 1.3,
    "actualización": 1.2, "recuperación": 1.5,
}

BEARISH_KEYWORDS = {
    # Inglés — alta señal
    "crash": 2.5, "dump": 2, "bearish": 2, "plunge": 2, "collapse": 2.5,
    "hack": 2.5, "exploit": 2.5, "rug pull": 3, "rugpull": 3,
    "scam": 2.5, "fraud": 2.5, "bankrupt": 2.5,
    # Inglés — media señal
    "drop": 1.5, "fall": 1.3, "decline": 1.5, "sell-off": 2,
    "selloff": 2, "ban": 2, "restrict": 1.5, "lawsuit": 2,
    "sue": 1.8, "sec": 1.5, "warning": 1.5, "risk": 1.2,
    "fear": 1.3, "delay": 1.3, "postpone": 1.3, "reject": 1.8,
    "rejected": 1.8, "fine": 1.5, "penalty": 1.5, "investigation": 1.5,
    "outflow": 1.5, "liquidation": 1.8, "fud": 1.5, "panic": 1.8,
    "concern": 1, "trouble": 1.3, "loss": 1.3, "losses": 1.3,
    "vulnerability": 2, "breach": 2, "theft": 2, "stolen": 2,
    "regulation": 1.2, "crackdown": 1.8, "sanction": 1.5,
    "red": 1, "sell": 1, "weak": 1, "bearmarket": 2,
    # Español
    "cae": 1.5, "caída": 1.5, "bajista": 2, "mínimo": 1.5,
    "negativo": 1, "hackeo": 2.5, "estafa": 2.5, "demanda": 1.8,
    "prohibición": 2, "riesgo": 1.2, "fraude": 2.5,
    "liquidación": 1.8, "pérdida": 1.3, "colapso": 2.5,
    "bancarrota": 2.5, "regulación": 1.2,
}

# Peso de las fuentes
SOURCE_WEIGHTS = {
    "coindesk": 1.4,
    "cointelegraph": 1.4,
    "the block": 1.3,
    "decrypt": 1.2,
    "bitcoin magazine": 1.2,
    "the defiant": 1.1,
    "bloomberg": 1.5,
    "reuters": 1.5,
    "cnbc": 1.3,
    "forbes": 1.2,
    "google news": 0.9,
    "cryptocompare": 1.0,
}


def _keyword_score(text: str) -> float:
    """
    Calcula score de sentimiento basado en palabras clave ponderadas.
    Retorna valor entre -1.0 y +1.0.
    """
    text_lower = text.lower()

    bullish_score = sum(
        weight for kw, weight in BULLISH_KEYWORDS.items()
        if kw in text_lower
    )
    bearish_score = sum(
        weight for kw, weight in BEARISH_KEYWORDS.items()
        if kw in text_lower
    )

    total = bullish_score + bearish_score
    if total == 0:
        return 0.0

    return (bullish_score - bearish_score) / total


def _source_weight(source: str) -> float:
    """Peso de confianza según la fuente."""
    source_lower = source.lower()
    for name, weight in SOURCE_WEIGHTS.items():
        if name in source_lower:
            return weight
    return 1.0


def analyze_news_sentiment(news_items: list[dict]) -> dict:
    """
    Analiza el sentimiento de una lista de noticias.

    Retorna:
        {
            "score": float (-100 a +100),
            "label": "ALCISTA" | "BAJISTA" | "NEUTRAL",
            "bullish_count": int,
            "bearish_count": int,
            "neutral_count": int,
            "top_news": list[dict],   # Las 3 noticias más relevantes
            "summary": str,           # Resumen del sentimiento
        }
    """
    if not news_items:
        return {
            "score": 0,
            "label": "NEUTRAL",
            "bullish_count": 0,
            "bearish_count": 0,
            "neutral_count": 0,
            "top_news": [],
            "summary": "Sin noticias disponibles",
        }

    total_score = 0.0
    total_weight = 0.0
    bullish_count = 0
    bearish_count = 0
    neutral_count = 0
    scored_news = []

    for item in news_items:
        title = item.get("title", "")
        body = item.get("body", "")
        source = item.get("source", "")
        weight = _source_weight(source)

        # Analizar título (peso 70%) + cuerpo (peso 30%)
        title_score = _keyword_score(title)
        body_score = _keyword_score(body) if body else 0.0
        combined = (title_score * 0.7 + body_score * 0.3) * weight

        total_score += combined
        total_weight += weight

        # Clasificar
        if combined > 0.08:
            bullish_count += 1
            item_label = "🟢"
        elif combined < -0.08:
            bearish_count += 1
            item_label = "🔴"
        else:
            neutral_count += 1
            item_label = "⚪"

        scored_news.append({
            **item,
            "score": round(combined, 3),
            "label": item_label,
        })

    # Score final normalizado a -100 / +100
    if total_weight > 0:
        raw_score = total_score / total_weight
    else:
        raw_score = 0.0

    final_score = max(-100, min(100, round(raw_score * 100)))

    # Label
    if final_score > 20:
        label = "ALCISTA"
    elif final_score < -20:
        label = "BAJISTA"
    else:
        label = "NEUTRAL"

    # Top noticias (por |score| más alto)
    top_news = sorted(scored_news, key=lambda x: abs(x["score"]), reverse=True)[:3]

    # Resumen
    total_news = len(news_items)
    summary = (
        f"{total_news} noticias analizadas: "
        f"{bullish_count} alcistas, {bearish_count} bajistas, "
        f"{neutral_count} neutrales"
    )

    logger.info(f"Sentimiento: {label} ({final_score}) — {summary}")

    return {
        "score": final_score,
        "label": label,
        "bullish_count": bullish_count,
        "bearish_count": bearish_count,
        "neutral_count": neutral_count,
        "top_news": top_news,
        "summary": summary,
    }
