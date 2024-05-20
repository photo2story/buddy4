#### get_ticker.py


import pandas as pd
import csv
import requests
import yfinance as yf
import investpy
import FinanceDataReader as fdr

def get_ticker_name(ticker, file_path='stock_market.csv'):
    df = pd.read_csv(file_path)
    result = df.loc[df['Symbol'] == ticker, 'Name']
    return result.iloc[0] if not result.empty else None

def get_ticker_market(ticker, file_path='stock_market.csv'):
    df = pd.read_csv(file_path)
    result = df.loc[df['Symbol'] == ticker, 'Market']
    return result.iloc[0] if not result.empty else None

def get_stock_info(ticker):
    info = yf.Ticker(ticker).info
    return {
        'Stock': ticker,
        'Industry': info.get('industry'),
        'Beta': info.get('beta'),
        'Sector': info.get('sector')
    }

def update_stock_market_csv(file_path, tickers_to_update):
    tickers_info = {ticker: get_stock_info(ticker) for ticker in tickers_to_update}
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    for i, row in df.iterrows():
        ticker = row['Symbol']
        if ticker in tickers_to_update:
            stock_info = tickers_info[ticker]
            for key, value in stock_info.items():
                df.at[i, key] = value
    df.to_csv(file_path, index=False, encoding='utf-8-sig')

def load_tickers(file_path='stock_market.csv'):
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    ticker_dict = {row['Name']: row['Symbol'] for _, row in df.iterrows()}
    return ticker_dict

def search_tickers(stock_name, ticker_dict):
    stock_name_lower = stock_name.lower() # convert to lower case
    return [(ticker, name) for name, ticker in ticker_dict.items() if stock_name_lower in name.lower()]
    #설명: stock_name_lower가 name에 포함되어 있으면 ticker와 name을 반환

def search_ticker_list_KR():
    url = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13'
    response = requests.get(url)
    response.encoding = 'euc-kr'
    df_listing = pd.read_html(response.text, header=0)[0]
    df_listing = df_listing.rename(columns={'회사명':'Name', '종목코드':'Symbol', '업종':'Sector'})
    df_listing['market'] = 'KRX'
    df_listing['Symbol'] = df_listing['Symbol'].apply(lambda x: '{:06d}'.format(x))
    return df_listing[['Symbol', 'Name', 'market', 'Sector']]

def search_ticker_list_US():
    df_amex = fdr.StockListing('AMEX')
    df_nasdaq = fdr.StockListing('NASDAQ')
    df_nyse = fdr.StockListing('NYSE')
    try:
        df_ETF_US = fdr.StockListing("ETF/US")
        df_ETF_US['market'] = "us_ETF"
    except Exception as e:
        print(f"An error occurred while fetching US ETF listings: {e}")
        df_ETF_US = pd.DataFrame(columns=['Symbol', 'Name', 'market'])
    df_amex['market'] = "AMEX"
    df_nasdaq['market'] = "NASDAQ"
    df_nyse['market'] = "NYSE"
    columns_to_select = ['Symbol', 'Name', 'market']
    df_amex = df_amex[columns_to_select]
    df_nasdaq = df_nasdaq[columns_to_select]
    df_nyse = df_nyse[columns_to_select]
    data_frames_US = [df_nasdaq, df_nyse, df_amex, df_ETF_US]
    df_US = pd.concat(data_frames_US, ignore_index=True)
    df_US['Sector'] = 'none'
    return df_US[['Symbol', 'Name', 'market', 'Sector']]

def search_ticker_list_US_ETF():
    df_etfs = investpy.etfs.get_etfs(country='united states')
    df_US_ETF = df_etfs[['symbol', 'name']].copy()
    df_US_ETF['market'] = 'US_ETF'
    df_US_ETF['Sector'] = 'US_ETF'
    df_US_ETF.columns = ['Symbol', 'Name', 'market', 'Sector']
    return df_US_ETF

def get_ticker_list_all():
    df_KR = search_ticker_list_KR()
    df_US = search_ticker_list_US()
    df_US_ETF = search_ticker_list_US_ETF()
    df_combined = pd.concat([df_KR, df_US, df_US_ETF], ignore_index=True)
    df_combined.to_csv('stock_market.csv', encoding='utf-8-sig', index=False)
    return df_combined

if __name__ == "__main__":
    tickers_to_update = [
        'VOO', 'QQQ', 'AAPL', 'GOOGL', 'MSFT', 'U', 'SPOT', 'PLTR', 'ADBE', 'TSLA', 'APTV',
        'FSLR', 'PFE', 'INMD', 'UNH', 'TDOC', 'OXY', 'FSLR', 'ALB', 'AMZN', 'NFLX', 'LLY', 'EL',
        'NKE', 'LOW', 'ADSK', 'NIO', 'F', 'BA', 'GE', 'JPM', 'BAC', 'SQ', 'HD', 'PG', 'IONQ', 'NVDA', 'AMD'
    ]
    file_path = 'stock_market.csv'
    update_stock_market_csv(file_path, tickers_to_update)
    info = get_stock_info('AAPL')
    print(info)
    market = get_ticker_market('086520', file_path='stock_market.csv')
    print(market)

