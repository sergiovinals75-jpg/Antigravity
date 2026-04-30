"""
CRYPTO SIGNAL BOT — Punto de entrada principal.

Flujo de ejecución:
  1. Obtener resumen global del mercado
  2. Para cada moneda rastreada:
     a. Obtener noticias (CryptoPanic + RSS)
     b. Analizar sentimiento
     c. Calcular RSI
     d. Generar señal (solo si hay confluencia)
  3. Construir informe
  4. Enviar por Telegram
"""
import sys
import time
import logging
from datetime import datetime, timezone, timedelta

from bot.config import TRACKED_COINS, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from bot.news_fetcher import get_all_news
from bot.rsi_calculator import get_rsi_analysis
from bot.sentiment_analyzer import analyze_news_sentiment
from bot.signal_engine import generate_signal
from bot.market_overview import get_market_overview
from bot.telegram_notifier import build_report, send_message

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("CryptoSignalBot")


def run():
    """Ejecuta el análisis completo y envía el informe."""

    # Zona horaria España (UTC+2 CEST)
    tz_spain = timezone(timedelta(hours=2))
    now = datetime.now(tz_spain)
    date_str = now.strftime("%d/%m/%Y — %H:%M CEST")

    logger.info("=" * 60)
    logger.info(f"🤖 CRYPTO SIGNAL BOT — {date_str}")
    logger.info("=" * 60)

    # Validar configuración
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error(
            "❌ Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID.\n"
            "   Configúralos en .env o en los Secrets de GitHub."
        )
        sys.exit(1)

    # ── 1. Resumen del mercado global ──
    logger.info("📊 Obteniendo datos globales del mercado…")
    market_overview = get_market_overview()
    logger.info(
        f"   Fear & Greed: {market_overview['fear_greed']['value']} "
        f"({market_overview['fear_greed']['label']})"
    )

    # ── 2. Analizar cada moneda ──
    all_signals = []
    total_coins = len(TRACKED_COINS)

    for idx, (symbol, coin_info) in enumerate(TRACKED_COINS.items(), 1):
        coin_id = coin_info["id"]
        coin_name = coin_info["name"]

        logger.info(f"\n[{idx}/{total_coins}] 🔍 Analizando {symbol} ({coin_name})…")

        # 2a. Obtener noticias
        logger.info(f"   📰 Buscando noticias…")
        news = get_all_news(symbol, coin_name)

        # 2b. Analizar sentimiento
        logger.info(f"   🧠 Analizando sentimiento…")
        sentiment = analyze_news_sentiment(news)
        logger.info(
            f"   → Sentimiento: {sentiment['label']} ({sentiment['score']:+d}) "
            f"[{sentiment['bullish_count']}↑ {sentiment['bearish_count']}↓ "
            f"{sentiment['neutral_count']}—]"
        )

        # 2c. Análisis técnico (RSI + precio)
        logger.info(f"   📈 Calculando RSI…")
        rsi_data = get_rsi_analysis(coin_id)
        logger.info(
            f"   → RSI: {rsi_data['rsi']} ({rsi_data['rsi_zone']}) "
            f"| Precio: ${rsi_data['current_price']}"
        )

        # 2d. Generar señal
        signal_result = generate_signal(symbol, rsi_data, sentiment)
        signal_result["top_news"] = sentiment.get("top_news", [])

        if signal_result["signal"] != "SIN SEÑAL":
            logger.info(
                f"   🚨 ¡SEÑAL! {signal_result['signal']} "
                f"(Confianza: {signal_result['confidence']})"
            )
        else:
            logger.info(f"   ⛔ Sin señal")

        all_signals.append(signal_result)

        # Rate-limiting entre monedas
        if idx < total_coins:
            time.sleep(1)

    # ── 3. Construir informe ──
    logger.info("\n📝 Construyendo informe…")
    report = build_report(market_overview, all_signals, date_str)

    # ── 4. Enviar por Telegram ──
    logger.info("📤 Enviando a Telegram…")
    success = send_message(report)

    if success:
        active = [s for s in all_signals if s["signal"] != "SIN SEÑAL"]
        logger.info(
            f"\n✅ Informe enviado correctamente.\n"
            f"   Señales activas: {len(active)}/{total_coins}\n"
            f"   Largos: {sum(1 for s in active if s['signal'] == 'LARGO')}\n"
            f"   Cortos: {sum(1 for s in active if s['signal'] == 'CORTO')}"
        )
    else:
        logger.error("❌ Error enviando el informe a Telegram")
        sys.exit(1)

    logger.info("=" * 60)
    logger.info("🏁 Análisis completado")
    logger.info("=" * 60)


if __name__ == "__main__":
    run()
