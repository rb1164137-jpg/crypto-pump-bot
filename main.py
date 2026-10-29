import time
import requests
import ccxt
import pandas as pd
import pandas_ta as ta

TELEGRAM_BOT_TOKEN = "9002885171:AAGoI8EInkvAf_fwdOfmUOVVvGdotRX3-YY"
TELEGRAM_CHAT_ID = "6585132254"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram Alert Error: {e}")

exchange = ccxt.binance({'enableRateLimit': True})

WATCHLIST = [
    'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'DOGE/USDT',
    'XRP/USDT', 'ADA/USDT', 'AVAX/USDT', 'NEAR/USDT', 'SUI/USDT',
    'PEPE/USDT', 'SHIB/USDT', 'FET/USDT', 'RENDER/USDT'
]

TIMEFRAME = '15m'

def analyze_symbol(symbol):
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=50)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])

        df['rsi'] = ta.rsi(df['close'], length=14)
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        df['vol_ma'] = ta.sma(df['volume'], length=20)

        current_close = float(df['close'].iloc[-1])
        current_open = float(df['open'].iloc[-1])
        current_volume = float(df['volume'].iloc[-1])
        avg_volume = float(df['vol_ma'].iloc[-1])
        current_rsi = float(df['rsi'].iloc[-1])
        current_atr = float(df['atr'].iloc[-1])

        volume_spike = current_volume > (avg_volume * 2.2)
        rsi_bullish = 55 <= current_rsi <= 75
        green_candle = current_close > current_open

        if volume_spike and rsi_bullish and green_candle:
            sl = current_close - (1.5 * current_atr)
            tp1 = current_close + (1.5 * current_atr)
            tp2 = current_close + (3.0 * current_atr)
            tp3 = current_close + (5.0 * current_atr)

            expected_pump_min = ((tp1 - current_close) / current_close) * 100
            expected_pump_max = ((tp3 - current_close) / current_close) * 100
            vol_multiplier = round(current_volume / avg_volume, 1)

            message = (
                f"🚨 *PUMP SIGNAL DETECTED* 🚨\n\n"
                f"🪙 *Coin:* `{symbol}` ({TIMEFRAME})\n"
                f"💵 *Live Entry:* `${current_close:.4f}`\n"
                f"🚀 *Expected Pump:* `+{expected_pump_min:.1f}% to +{expected_pump_max:.1f}%`\n\n"
                f"🎯 *Targets (TP):*\n"
                f"• TP 1: `${tp1:.4f}` (+{expected_pump_min:.1f}%)\n"
                f"• TP 2: `${tp2:.4f}`\n"
                f"• TP 3: `${tp3:.4f}` (+{expected_pump_max:.1f}%)\n\n"
                f"🛑 *Stop Loss (SL):* `${sl:.4f}`\n\n"
                f"📊 *Volume Spike:* `{vol_multiplier}x`\n"
                f"⚡ *RSI:* `{current_rsi:.1f}`\n"
                f"⚠️ *Trade with strict risk management!*"
            )

            print(f"[!] Signal: {symbol}")
            send_telegram_alert(message)
    except Exception as e:
        print(f"Error on {symbol}: {e}")

def start_bot():
    print("Bot cloud par start ho chuka hai...")
    send_telegram_alert("🤖 *AI 24/7 Pump Scanner Cloud Par Online Hai!*")
    while True:
        for symbol in WATCHLIST:
            analyze_symbol(symbol)
            time.sleep(1)
        time.sleep(90)

if __name__ == "__main__":
    start_bot()
