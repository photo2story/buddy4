import pandas as pd
import requests
import discord
import os
from discord.ext import commands
import pprint

def get_ranking_alpha():
    # Alpha Vantage API에서 데이터 가져오기
    # JSON 데이터를 가져옵니다.
    url = 'https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey=Alpha_Vantage_API'
    r = requests.get(url)
    data = r.json()
  
    # 필요한 데이터만 추출합니다.
    last_updated = data.get('last_updated')
    top_gainers = data.get('top_gainers')
    top_losers = data.get('top_losers')
    most_actively_traded = data.get('most_actively_traded')
  
    # 데이터를 데이터프레임으로 변환합니다.
    df_last_updated = pd.DataFrame([last_updated], columns=['Remarks'])
    df_top_gainers = pd.DataFrame(top_gainers)
    df_top_gainers['Remarks'] = 'Top Gainers'
    df_top_losers = pd.DataFrame(top_losers)
    df_top_losers['Remarks'] = 'Top Losers'
    df_most_actively_traded = pd.DataFrame(most_actively_traded)
    df_most_actively_traded['Remarks'] = 'Most Actively Traded'
  
    # 모든 데이터프레임을 하나로 통합합니다.
    # df_combined = pd.concat([df_last_updated, df_top_gainers, df_top_losers, df_most_actively_traded], ignore_index=True)
    df_combined = pd.concat([df_last_updated, df_top_gainers, df_most_actively_traded], ignore_index=True)
    # NaN 값을 포함한 행을 삭제합니다.
    df_combined = df_combined.dropna()
    df_most_actively_traded = df_most_actively_traded.dropna()
    # print(df_combined)
    # print(df_most_actively_traded)
  
    # 데이터프레임을 요약한 텍스트 생성
    summary_text = "종합 랭킹 정보:\n" + df_combined.head().to_string(index=False)
    # print(summary_text)

    # 문자열로 변환하여 반환
    return df_most_actively_traded
