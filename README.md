# 🤖 Crypto Signal Bot

Bot de señales de trading crypto que analiza noticias fundamentales + RSI técnico y envía señales por Telegram.

**Solo genera señal cuando hay CONFLUENCIA:**
- 🟢 **LARGO**: RSI en sobreventa (< 30) + noticias alcistas
- 🔴 **CORTO**: RSI en sobrecompra (> 70) + noticias bajistas
- ⛔ **Sin señal**: Si no hay confluencia, no opera

## 📊 Qué analiza

| Fuente | Datos |
|--------|-------|
| **CryptoPanic** | Noticias agregadas de CoinDesk, CoinTelegraph, The Block, Decrypt… |
| **RSS Feeds** | CoinDesk, CoinTelegraph, Decrypt, Bitcoin Magazine, The Defiant |
| **CoinGecko** | Precios, RSI, capitalización, trending |
| **Alternative.me** | Índice Fear & Greed |

### Monedas rastreadas
BTC, ETH, BNB, SOL, XRP, ADA, DOGE, AVAX, DOT, LINK, MATIC, UNI, ATOM, NEAR, APT, ARB, SUI

## 🚀 Instalación en GitHub

### 1. Crear repositorio en GitHub

1. Ve a [github.com/new](https://github.com/new)
2. Nombre: `crypto-signal-bot` (o el que prefieras)
3. Privado ✅
4. Crea el repositorio

### 2. Subir los archivos

```bash
cd crypto-signal-bot
git init
git add .
git commit -m "🤖 Initial commit - Crypto Signal Bot"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/crypto-signal-bot.git
git push -u origin main
```

### 3. Configurar Secrets en GitHub

Ve a tu repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

| Secret | Descripción | Cómo obtenerlo |
|--------|-------------|----------------|
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram | Habla con [@BotFather](https://t.me/BotFather) → `/newbot` |
| `TELEGRAM_CHAT_ID` | Tu ID de chat en Telegram | Habla con [@userinfobot](https://t.me/userinfobot) → `/start` |
| `CRYPTOPANIC_API_KEY` | API key de CryptoPanic (opcional) | Regístrate gratis en [cryptopanic.com/developers/api](https://cryptopanic.com/developers/api/) |

### 4. Activar GitHub Actions

1. Ve a la pestaña **Actions** de tu repositorio
2. Si aparece un aviso, haz clic en **"I understand my workflows, go ahead and enable them"**
3. El bot se ejecutará automáticamente cada día a las **09:00 hora España (CEST)**

### 5. Ejecutar manualmente (para probar)

1. Ve a **Actions** → **"🤖 Crypto Signal Bot — Daily Analysis"**
2. Clic en **"Run workflow"** → **"Run workflow"**
3. Espera ~2 minutos y revisa tu Telegram

## 📱 Ejemplo de mensaje en Telegram

```
🤖 CRYPTO SIGNAL BOT
📅 30/04/2026 — 09:00 CEST
━━━━━━━━━━━━━━━━━━━━━━━━━

🌍 MERCADO GLOBAL
├ Cap. Total: $2.45T
├ Vol. 24h: $89.32B
├ BTC Dom: 52.3%
├ ETH Dom: 17.8%
├ Cambio 24h: 📈 +1.25%
└ Fear&Greed: 35 — Miedo 😰
  [███░░░░░░░] 35/100

━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 SEÑALES ACTIVAS (1)

┌─────────────────────────
│ BTC/USDT
├ 💰 Precio: $67,450.00
├ 24h: 📉 -3.25%
├ 🔻 RSI(14): 28.5 (SOBREVENTA)
├ 📰🟢 Sentimiento: ALCISTA (+45)
├ ✅ Señal: 🟢 LARGO (LONG)
├ 📊 Confianza: ALTA 🟢🟢🟢
├ 💡 CONFLUENCIA ALCISTA:
│   • RSI en zona de SOBREVENTA
│   • Noticias fundamentales positivas
└─────────────────────────
```

## ⚙️ Configuración avanzada

### Ajustar monedas rastreadas

Edita `bot/config.py` → `TRACKED_COINS` para añadir o quitar monedas.

### Cambiar horario

Edita `.github/workflows/daily_signal.yml` → el campo `cron`:

```yaml
# Ejemplos:
- cron: "0 7 * * *"    # 09:00 CEST (verano España)
- cron: "0 7 * * 1-5"  # Solo lunes a viernes
- cron: "0 6 * * *"    # 08:00 CEST
```

### Ajustar sensibilidad RSI

En `bot/config.py`:
```python
RSI_OVERBOUGHT = 70   # Subir = menos señales de CORTO
RSI_OVERSOLD = 30      # Bajar = menos señales de LARGO
```

### Ajustar sensibilidad sentimiento

En `bot/config.py`:
```python
SENTIMENT_BULLISH_THRESHOLD = 30    # Subir = más exigente para LARGO
SENTIMENT_BEARISH_THRESHOLD = -30   # Bajar = más exigente para CORTO
```

## 📁 Estructura del proyecto

```
crypto-signal-bot/
├── .github/workflows/
│   └── daily_signal.yml    ← Cron job (09:00 CEST diario)
├── bot/
│   ├── config.py           ← Configuración y monedas
│   ├── news_fetcher.py     ← Obtención de noticias (CryptoPanic + RSS)
│   ├── rsi_calculator.py   ← Cálculo RSI con CoinGecko
│   ├── sentiment_analyzer.py ← Análisis de sentimiento
│   ├── signal_engine.py    ← Motor de señales (confluencia RSI + sentimiento)
│   ├── market_overview.py  ← Datos globales + Fear & Greed
│   └── telegram_notifier.py ← Envío y formato de mensajes
├── main.py                 ← Punto de entrada
├── requirements.txt        ← Dependencias Python
├── .env.example            ← Plantilla de variables de entorno
└── README.md               ← Este archivo
```

## ⚠️ Disclaimer

Este bot es una herramienta de análisis y **NO constituye consejo financiero**. Haz siempre tu propia investigación (DYOR) antes de operar. El trading de criptomonedas conlleva riesgos significativos.

## 📄 Licencia

Uso personal. No redistribuir.
