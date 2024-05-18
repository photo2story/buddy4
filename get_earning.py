import pandas as pd
import requests
import discord
import os
from discord.ext import commands
import pprint
import csv
import yfinance as yf
import datetime
from yahoo_earnings_calendar import YahooEarningsCalendar
import yahoo_fin.stock_info as si

def get_earning_alpha(symbol):
    # Yahoo Finance에서 수익 달력 데이터 가져오기
    # earning_data = si.get_next_earnings_date("aapl")
    #     # Returns a list of all available earnings of BOX
    # print(earning_data)

    # Alpha Vantage API에서 데이터 가져오기
    # API_KEY = "Your API key"
    horizon = "3month"
    data = []
  

    url = f"https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&symbol={symbol}&horizon={horizon}&apikey={'Alpha_Vantage_API'}"
    with requests.Session() as s:
        download = s.get(url)
        decoded_content = download.content.decode('utf-8')
        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        for row in my_list:
            data.append(row) 

    # 데이터에서 DataFrame을 생성합니다. list
    columns = ['Symbol'] + data[0][1:]  # Use the header from the first row
    df = pd.DataFrame(data[1:], columns=columns)
  
    # 'name' 값을 포함하는 행 제거
    df = df[~df.apply( lambda row: 'name'  in row.values, axis= 1 )] 
  
    # 중복된 열 'symbol'을 삭제합니다.
    df = df.loc[:, ~df.columns.duplicated()] 
  
    # 'reportDate' 열에서 값이 없음인 행을 제거합니다.
    df = df.dropna(subset=[ 'reportDate' ]) 
  
    # Save the DataFrame to a CSV file
    output_file_path = "earnig_data.csv"
    df.to_csv(output_file_path, index=False)
    # print(df)

  # 문자열로 변환하여 반환
    return df

def get_earnings_forecast(symbol):
  # Alpha Vantage API 키 설정
  api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
  horizon = "3month"
  
  # Earnings 데이터를 위한 API 요청 URL 구성
  url = f'https://www.alphavantage.co/query?function=EARNINGS&symbol={ticker}&apikey={api_key}'

  # API 요청
  response = requests.get(url)
  if response.status_code != 200:
      raise Exception("API 요청 실패")

  # JSON 응답 파싱
  data = response.json()

  # 어닝 데이터 추출 (예시: 연간 어닝 데이터)
  annual_earnings = data.get('annualEarnings', [])

  # DataFrame으로 변환
  df = pd.DataFrame(annual_earnings)

  return df

# 사용 예시
# 모듈을 직접 실행할 때만 아래 테스트 코드가 실행되도록 합니다.
if __name__ == "__main__":
    ticker = 'AAPL'
    df_earnings = get_earnings_forecast(ticker)
    # print(df_earnings)
    # df = get_earning_alpha(ticker)
    # print(df)