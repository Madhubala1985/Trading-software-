# main.py

from binance import ThreadedWebsocketManager
from binance.client import Client
from config import BINANCE_API_KEY, BINANCE_SECRET_KEY
from data_handler import PriceBuffer
import numpy as np

# Price-based strategies
from strategies.moving_average import moving_average_crossover
from strategies.rsi import rsi
from strategies.bollinger import bollinger_band

# Order-book strategies
from strategies.liquidity_trap import liquidity_trap_signal
from strategies.orderbook_imbalance import orderbook_imbalance_signal
from strategies.spread_reversion import spread_reversion_signal

# Advanced trade-based strategies
from strategies.iceberg_detector import iceberg_detector_signal
from strategies.vwap_signals import VWAPCalculator, vwap_signal
from strategies.volume_profile import VolumeProfile, volume_profile_signal
from strategies.kalman_filter import KalmanMeanReverter

# Pairs trading
from strategies.pairs_trading import PairTrader

# Funding-rate arbitrage
from strategies.funding_rate_arbitrage import funding_rate_arbitrage_signal

# News / sentiment strategies
from strategies.news_spike import news_spike_signal
from strategies.sentiment_cluster import SentimentCluster, sentiment_cluster_signal

# Deep-learning / pattern strategies
from strategies.cnn_pattern import CNNPatternDetector
from strategies.ts_transformer import TransformerForecast
from strategies.rl_executor import RLExecutor

# === Configuration ===
SYMBOL               = 'BTCUSDT'
PAIR_BASE            = 'BTCUSDT'
PAIR_QUOTE           = 'ETHUSDT'
PRICE_BUFFER_LEN     = 100
LIQUIDITY_THRESHOLD  = 200
IMBALANCE_TOP_N      = 5
IMBALANCE_THRESHOLD  = 0.6
ICEBERG_THRESHOLD    = 50
VWAP_THRESHOLD       = 0.002
VP_BUCKET_SIZE       = 1.0
VP_THRESHOLD         = 1.0
SPREAD_THRESHOLD     = 0.5
PAIR_WINDOW          = 100
PAIR_Z_THRESH        = 2.0
KALMAN_R             = 0.01
KALMAN_Q             = 1e-5
KALMAN_Z_THRESH      = 1.5
FUND_RATE_THRESH     = 0.001
NEWS_SPIKE_THRESH    = 0.8
NEWS_COOLDOWN        = 300
SENT_CLUSTER_WINDOW  = 20
VOL_THRESHOLD        = 0.02
CLUSTER_THRESHOLD    = 0.3

# DL model paths (replace with your actual model files)
CNN_MODEL_PATH       = 'models/cnn_pattern.pt'
TS_MODEL_PATH        = 'models/ts_transformer.pth'
RL_MODEL_PATH        = 'models/rl_executor.model'

# === Init REST & State ===
rest_client     = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
price_buffer    = PriceBuffer(maxlen=PRICE_BUFFER_LEN)
last_order_book = {'bids': [], 'asks': []}
vwap_calc       = VWAPCalculator()
vp              = VolumeProfile(bucket_size=VP_BUCKET_SIZE)
kalman          = KalmanMeanReverter(R=KALMAN_R, Q=KALMAN_Q)
pair_trader     = PairTrader([], [], window=PAIR_WINDOW, z_thresh=PAIR_Z_THRESH)
sent_cluster    = SentimentCluster(window=SENT_CLUSTER_WINDOW)
cnn_detector    = CNNPatternDetector(CNN_MODEL_PATH)
ts_forecast     = TransformerForecast(TS_MODEL_PATH)
rl_agent        = RLExecutor(RL_MODEL_PATH)
last_prices     = {}

def get_price_trend(prices):
    if len(prices) < 2:
        return 0
    return 1 if prices[-1] > prices[-2] else -1

def fetch_funding_rate(symbol):
    data = rest_client.futures_funding_rate(symbol=symbol, limit=1)
    return float(data[0]['fundingRate']) if data else None

def compute_volatility(prices):
    if len(prices) < 2:
        return 0
    returns = np.diff(prices) / prices[:-1]
    return float(np.std(returns))

def handle_trade_message(msg):
    """Called on each trade update for BTC and ETH."""
    try:
        sym   = msg['s']
        price = float(msg['p'])
        qty   = float(msg['q'])

        # Update for pairs trading
        if sym in (PAIR_BASE, PAIR_QUOTE):
            last_prices[sym] = price

        # Only run core signals on BTC
        if sym == SYMBOL:
            price_buffer.add_price(price)
            prices = price_buffer.get_prices()

            # Basic TA
            ma_sig  = moving_average_crossover(prices)
            rsi_sig = rsi(prices)
            bb_sig  = bollinger_band(prices)

            # Order-book & trade-based
            ice_sig  = iceberg_detector_signal(msg, last_order_book, size_threshold=ICEBERG_THRESHOLD)
            vwap_sig = vwap_signal(msg, vwap_calc, threshold=VWAP_THRESHOLD)
            vp_sig   = volume_profile_signal(msg, vp, threshold=VP_THRESHOLD)
            kal_sig  = kalman.signal(price, entry_z=KALMAN_Z_THRESH)

            # Pairs Trading
            pair_sig = None
            if PAIR_BASE in last_prices and PAIR_QUOTE in last_prices:
                pair_sig = pair_trader.signal(last_prices[PAIR_BASE], last_prices[PAIR_QUOTE])

            # Funding-Rate Arbitrage
            funding_rate = fetch_funding_rate(SYMBOL)
            trend        = get_price_trend(prices)
            fund_sig     = funding_rate_arbitrage_signal(funding_rate, trend, rate_threshold=FUND_RATE_THRESH)

            # Sentiment/News (replace sentiment_score with your NLP output)
            sentiment_score = 0.0
            news_sig = news_spike_signal(sentiment_score, spike_threshold=NEWS_SPIKE_THRESH, cooldown=NEWS_COOLDOWN)
            vol      = compute_volatility(prices)
            sent_sig = sentiment_cluster_signal(
                sentiment_score, vol, sent_cluster,
                vol_threshold=VOL_THRESHOLD, cluster_threshold=CLUSTER_THRESHOLD
            )

            # Deep-learning signals
            cnn_sig = cnn_detector.signal(prices)
            ts_sig  = ts_forecast.signal(prices, threshold=VWAP_THRESHOLD)
            # Prepare state for RL agent
            state = {
                'prices': prices,
                'order_book': last_order_book,
                'indicators': {
                    'ma': ma_sig, 'rsi': rsi_sig, 'bb': bb_sig,
                    'ice': ice_sig, 'vwap': vwap_sig, 'vp': vp_sig, 'kal': kal_sig
                }
            }
            rl_sig = rl_agent.signal(state)

            print(
                f"[TRADE:{sym}] Price:{price:>8.2f} | "
                f"MA:{ma_sig or '…':>4} RSI:{rsi_sig or '…':>4} BB:{bb_sig or '…':>4} | "
                f"ICE:{ice_sig:>4} VWAP:{vwap_sig:>4} VP:{vp_sig:>4} KAL:{kal_sig or '…':>4} | "
                f"PAIR:{pair_sig or '…':>8} FUND:{fund_sig:>4} NEWS:{news_sig:>4} SENT:{sent_sig:>4} | "
                f"CNN:{cnn_sig:>4} TS:{ts_sig:>4} RL:{rl_sig:>4}"
            )
    except Exception as e:
        print(f"Error in handle_trade_message: {e}")

def handle_depth_message(msg):
    """Called on each order-book update for BTC."""
    global last_order_book
    try:
        last_order_book = msg

        lt_sig     = liquidity_trap_signal(msg, threshold=LIQUIDITY_THRESHOLD)
        imb_sig    = orderbook_imbalance_signal(msg, top_n=IMBALANCE_TOP_N, imbalance_threshold=IMBALANCE_THRESHOLD)
        spread_sig = spread_reversion_signal(msg, spread_threshold=SPREAD_THRESHOLD)

        print(f"[BOOK ] LT:{lt_sig:>4} IMB:{imb_sig:>4} SPR:{spread_sig:>4}")
    except Exception as e:
        print(f"Error in handle_depth_message: {e}")

def main():
    twm = ThreadedWebsocketManager(api_key=BINANCE_API_KEY, api_secret=BINANCE_SECRET_KEY)
    twm.start()

    # Stream trades for both pairs
    twm.start_trade_socket(callback=handle_trade_message, symbol=PAIR_BASE)
    twm.start_trade_socket(callback=handle_trade_message, symbol=PAIR_QUOTE)

    # Stream order-book updates
    twm.start_depth_socket(callback=handle_depth_message, symbol=SYMBOL, depth=IMBALANCE_TOP_N)

    print("Streaming data… Press Enter to stop.")
    input()
    twm.stop()

if __name__ == "__main__":
    main()
