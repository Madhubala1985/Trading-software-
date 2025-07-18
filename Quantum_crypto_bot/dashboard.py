import streamlit as st
import pandas as pd
from binance.client import Client
from config import BINANCE_API_KEY, BINANCE_SECRET_KEY

client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

st.title('Binance Live Price Stream')

symbol = st.selectbox('Select symbol', ['BTCUSDT', 'ETHUSDT', 'BNBUSDT'])
depth = client.get_order_book(symbol=symbol)
trades = client.get_recent_trades(symbol=symbol)

prices = [float(trade['price']) for trade in trades]
df = pd.DataFrame({'Price': prices})

st.line_chart(df['Price'])

st.subheader('Order Book (Top 5)')
bids = depth['bids'][:5]
asks = depth['asks'][:5]
st.write('**Bids:**', bids)
st.write('**Asks:**', asks)
