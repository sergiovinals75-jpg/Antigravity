"""
Notificador Telegram — envía el informe de señales formateado.
Usa la API de Telegram Bot directamente (sin dependencias extra).
"""
import logging
import requests

from bot.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

logger = logging.getLogger(__name__)

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
MAX_MESSAGE_LENGTH = 4096  # Límite de Telegram


def send_message(text: str, parse_mode: str = "HTML") -> bool:
    """Envía un mensaje por Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("❌ TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no configurados")
        return False

    # Dividir mensajes largos
    chunks = _split_message(text, MAX_MESSAGE_LENGTH)

    for chunk in chunks:
        try:
            resp = requests.post(
                f"{TELEGRAM_API}/sendMessage",
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": chunk,
                    "parse_mode": parse_mode,
                    "disable_web_page_preview": True,
                },
                timeout=30,
            )
            resp.raise_for_status()
            logger.info("✅ Mensaje enviado a Telegram")
        except Exception as e:
            logger.error(f"❌ Error enviando a Telegram: {e}")
            # Intentar sin parse_mode si falla el HTML
            try:
                resp = requests.post(
                    f"{TELEGRAM_API}/sendMessage",
                    json={
                        "chat_id": TELEGRAM_CHAT_ID,
                        "text": chunk,
                        "disable_web_page_preview": True,
                    },
                    timeout=30,
                )
                resp.raise_for_status()
            except Exception as e2:
                logger.error(f"❌ Error enviando (sin formato): {e2}")
                return False

    return True


def _split_message(text: str, max_length: int) -> list[str]:
    """Divide mensaje largo en chunks respetando saltos de línea."""
    if len(text) <= max_length:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break

        # Buscar el último salto de línea dentro del límite
        split_at = text.rfind("\n", 0, max_length)
        if split_at == -1:
            split_at = max_length

        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")

    return chunks


def format_price(price: float | None) -> str:
    """Formatea precio según magnitud."""
    if price is None:
        return "N/A"
    if price >= 1000:
        return f"${price:,.2f}"
    elif price >= 1:
        return f"${price:.4f}"
    else:
        return f"${price:.6f}"


def format_change(change: float | None) -> str:
    """Formatea cambio porcentual con emoji."""
    if change is None:
        return "N/A"
    emoji = "📈" if change >= 0 else "📉"
    return f"{emoji} {change:+.2f}%"


def build_report(
    market_overview: dict,
    signals: list[dict],
    date_str: str,
) -> str:
    """
    Construye el informe completo de señales para Telegram.
    """
    # ── Cabecera ──
    report = (
        f"🤖 <b>CRYPTO SIGNAL BOT</b>\n"
        f"📅 {date_str}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    # ── Resumen del mercado ──
    fg = market_overview.get("fear_greed", {})
    fg_value = fg.get("value")
    fg_bar = _progress_bar(fg_value) if fg_value else ""

    from bot.market_overview import format_market_cap

    report += (
        f"🌍 <b>MERCADO GLOBAL</b>\n"
        f"├ Cap. Total: {format_market_cap(market_overview.get('total_market_cap'))}\n"
        f"├ Vol. 24h: {format_market_cap(market_overview.get('total_volume'))}\n"
        f"├ BTC Dom: {market_overview.get('btc_dominance', 'N/A')}%\n"
        f"├ ETH Dom: {market_overview.get('eth_dominance', 'N/A')}%\n"
        f"├ Cambio 24h: {format_change(market_overview.get('market_cap_change_24h'))}\n"
        f"└ Fear&Greed: {fg_value or 'N/A'} — {fg.get('label', 'N/A')}\n"
        f"  {fg_bar}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    # ── Señales activas ──
    active_signals = [s for s in signals if s["signal"] != "SIN SEÑAL"]

    if active_signals:
        report += f"🚨 <b>SEÑALES ACTIVAS ({len(active_signals)})</b>\n\n"

        for s in active_signals:
            signal_emoji = "🟢 LARGO (LONG)" if s["signal"] == "LARGO" else "🔴 CORTO (SHORT)"
            rsi_emoji = "🔻" if s["rsi_zone"] == "SOBREVENTA" else "🔺"
            sent_emoji = "📰🟢" if s["sentiment_label"] == "ALCISTA" else "📰🔴"

            report += (
                f"┌─────────────────────────\n"
                f"│ <b>{s['symbol']}/USDT</b>\n"
                f"├ 💰 Precio: {format_price(s['current_price'])}\n"
                f"├ 24h: {format_change(s['change_24h'])}\n"
                f"├ {rsi_emoji} RSI(14): <b>{s['rsi']}</b> ({s['rsi_zone']})\n"
                f"├ {sent_emoji} Sentimiento: <b>{s['sentiment_label']}</b> ({s['sentiment_score']:+d})\n"
                f"├ ✅ Señal: <b>{signal_emoji}</b>\n"
                f"├ 📊 Confianza: {s['confidence']} {s['confidence_emoji']}\n"
                f"├ 💡 {s['reasoning']}\n"
                f"└─────────────────────────\n\n"
            )
    else:
        report += "⛔ <b>SIN SEÑALES ACTIVAS HOY</b>\n\n"
        report += "No hay confluencia RSI + Sentimiento en ningún par.\n\n"

    # ── Resumen de todos los pares ──
    report += f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    report += f"📋 <b>RESUMEN TODOS LOS PARES</b>\n\n"

    for s in signals:
        if s["signal"] != "SIN SEÑAL":
            icon = "🟢" if s["signal"] == "LARGO" else "🔴"
        else:
            icon = "⚪"

        rsi_str = f"{s['rsi']}" if s['rsi'] is not None else "N/A"
        report += (
            f"{icon} <b>{s['symbol']}</b> — "
            f"RSI: {rsi_str} | "
            f"Sent: {s['sentiment_score']:+d} | "
            f"{format_price(s['current_price'])} "
            f"({format_change(s['change_24h'])})\n"
        )

    # ── Noticias destacadas ──
    report += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    report += f"📰 <b>NOTICIAS DESTACADAS</b>\n\n"

    # Recopilar top noticias de señales activas
    all_top_news = []
    for s in signals:
        top_news = s.get("top_news", [])
        for news in top_news:
            if news not in all_top_news:
                all_top_news.append(news)

    if all_top_news:
        for news in all_top_news[:8]:
            label = news.get("label", "⚪")
            title = news.get("title", "")[:80]
            source = news.get("source", "")
            report += f"{label} {title}\n   <i>— {source}</i>\n"
    else:
        report += "Sin noticias destacadas disponibles.\n"

    # ── Footer ──
    report += (
        f"\n━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠️ <i>Esto NO es consejo financiero.\n"
        f"Haz tu propia investigación (DYOR).</i>\n"
        f"🤖 Bot v1.0 | Análisis a las 09:00 CEST"
    )

    return report


def _progress_bar(value: int, length: int = 10) -> str:
    """Genera barra de progreso visual para Fear & Greed."""
    if value is None:
        return ""
    filled = round(value / 100 * length)
    bar = "█" * filled + "░" * (length - filled)
    return f"  [{bar}] {value}/100"
