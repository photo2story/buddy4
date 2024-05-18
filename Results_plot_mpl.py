
## Results_plot_mpl.py


import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas_ta as ta
import pandas as pd
import requests
import numpy as np
import FinanceDataReader as fdr
from datetime import datetime
import os
from get_ticker import get_ticker_name, get_ticker_market
from tradingview_ta import TA_Handler, Interval, Exchange

def convert_file_path_for_saving(file_path):
  return file_path.replace('/', '-')

def convert_file_path_for_reading(file_path):
  return file_path.replace('-', '/')

def save_figure(fig, file_path):
  file_path = convert_file_path_for_saving(file_path)
  fig.savefig(file_path)
  plt.close(fig)  # 닫지 않으면 메모리를 계속 차지할 수 있음

def get_tradingview_analysis(ticker):
  market = get_ticker_market(ticker, file_path='stock_market.csv')
  if market == 'KRX':
    screener = "korea"
  elif market == 'UPBIT' or market == 'BINANCE' :   
    screener = "crypto"
  else:   
    screener = "america"

  print(market)

  tv_handler = TA_Handler(
      symbol = ticker,
      exchange = market,
      screener = screener,
      interval = Interval.INTERVAL_1_DAY,
  )
  tv_analysis = tv_handler.get_analysis().summary
  return tv_analysis

def plot_results_mpl(ticker, start_date, end_date):
    prices = fdr.DataReader(ticker, start_date, end_date)
    prices.dropna(inplace=True)

    # Calculate SMA 20 and SMA 60
    SMA20 = prices['Close'].rolling(window=20).mean()
    SMA60 = prices['Close'].rolling(window=60).mean()

    # Calculate short and long EMA
    short_ema = prices['Close'].ewm(span=12, adjust=False).mean()
    long_ema = prices['Close'].ewm(span=26, adjust=False).mean()
    ppo = ((short_ema - long_ema) / long_ema) * 100
    ppo_signal = ppo.ewm(span=9, adjust=False).mean()

    # Calculate PPO Histogram with error handling
    try:
        ppo_histogram = ppo - ppo_signal
    except TypeError as e:
        print(f"Error calculating PPO Histogram: {e}")
        ppo_histogram = pd.Series(np.zeros(len(ppo)), index=ppo.index)

    # Plot using mplfinance
    fig, axes = mpf.plot(prices, type='candle', style='charles', volume=True, 
                         mav=(20, 60), returnfig=True)

    # Add PPO Histogram
    ax2 = axes[2]
    ax2.bar(ppo.index, ppo_histogram, color='b', label='PPO Histogram')

    # Save figure
    save_figure(fig, f'result_mpl_{ticker}.png')

    name = get_ticker_name(ticker)
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

    message = f"Stock: {ticker} ({name})\n" \
              f"Close 종가: {prices['Close'].iloc[-1]:,.2f}\n" \
              f"SMA 20: {SMA20.iloc[-1]:,.2f}\n" \
              f"SMA 60: {SMA60.iloc[-1]:,.2f}\n" \
              f"PPO Histogram: {ppo_histogram.iloc[-1]:,.2f}\n"
    response = requests.post(DISCORD_WEBHOOK_URL, data={'content': message})
    if response.status_code != 204:
       print('Discord 메시지 전송 실패')
    else:
       print('Discord 메시지 전송 성공')

    files = {'file': open(f'result_mpl_{ticker}.png', 'rb')}
    response = requests.post(DISCORD_WEBHOOK_URL, files=files)

if __name__ == "__main__":
    ticker = 'VOO'
    start_date = "2022-01-01"
    end_date = datetime.today().strftime('%Y-%m-%d')
    plot_results_mpl(ticker, start_date, end_date)
