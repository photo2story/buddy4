# main.py
    # 'AAPL', 'GOOGL', 'MSFT', 'U', 'SPOT', 'PLTR', 'ADBE', 'TSLA', 'APTV', 'FSLR', 'PFE', 'INMD', 'UNH',
    # 'TDOC', 'OXY', 'FSLR', 'ALB', 'AMZN', 'NFLX', 'LLY', 'EL', 'NKE', 'LOW', 'ADSK', 'NIO', 'F', 'BA', 'GE', 'JPM',
    # 'BAC', 'SQ', 'HD', 'PG', 'IONQ', '086520', 

from flask import Flask, request, jsonify
from threading import Thread
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
from datetime import datetime
import pandas as pd
import numpy as np
import requests
from discord.ext import tasks
from get_ticker import load_tickers, search_tickers, get_ticker_name,update_stock_market_csv
from estimate_stock import estimate_snp, estimate_stock
from Results_plot import plot_comparison_results, plot_results_all
from get_compare_stock_data import merge_csv_files, load_sector_info
from Results_plot_mpl import plot_results_mpl
import tracemalloc

load_dotenv()

app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

@app.route('/execute_stock_command', methods=['POST'])
def execute_stock_command():
    data = request.json
    stock_name = data.get('stock_name')
    if stock_name:
        asyncio.run(execute_stock(stock_name))
        return jsonify(success=True)
    return jsonify(success=False)

async def execute_stock(stock_name):
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        ctx = await bot.get_context(channel)
        await ctx.send(f'Processing stock: {stock_name}')
        await stock(ctx, stock_name)
        
def run():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))

def keep_alive():
    server = Thread(target=run)
    server.start()

keep_alive()

TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='', intents=intents)  # Remove prefix

@bot.event
async def on_ready():
    print(f'Bot이 성공적으로 로그인했습니다: {bot.user.name}')
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send(f'Bot이 성공적으로 로그인했습니다: {bot.user.name}')
    else:
        print(f"채널을 찾을 수 없습니다: {CHANNEL_ID}")

@bot.command()
async def ping(ctx):
    print(f"Ping command received from {ctx.author.name}")
    await ctx.send(f'pong: {bot.user.name}')

tracemalloc.start()

channel_id = os.getenv('DISCORD_CHANNEL_ID')

stocks = [
    'QQQ', 'MSFT', 'AAPL', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 
    'ADBE', 'JPM', 'F', 'BA', 'GE', 'UNH', 'PFE',
    'BAC', 'SQ', 'HD', 'PG', 'COIN', 'NFLX'
]

start_date = "2022-01-01"
end_date = datetime.today().strftime('%Y-%m-%d')
initial_investment = 30000000
monthly_investment = 1000000

async def backtest_and_send(ctx, stock, option_strategy):
    total_account_balance, total_rate, str_strategy, invested_amount, str_last_signal, min_stock_data_date, file_path, result_df = estimate_stock(
        stock, start_date, end_date, initial_investment, monthly_investment, option_strategy)
    min_stock_data_date = str(min_stock_data_date).split(' ')[0]
    user_stock_file_path1 = file_path

    file_path = estimate_snp(stock, 'VOO', min_stock_data_date, end_date, initial_investment, monthly_investment, option_strategy, result_df)
    user_stock_file_path2 = file_path

    name = get_ticker_name(stock)
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
    message = {
        'content': f"Stock: {stock} ({name})\n"
                   f"Total_rate: {total_rate:,.0f} %\n"
                   f"Invested_amount: {invested_amount:,.0f} $\n"
                   f"Total_account_balance: {total_account_balance:,.0f} $\n"
                   f"Last_signal: {str_last_signal} \n"
                   f" "
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=message)

    if response.status_code != 204:
        print('Discord 메시지 전송 실패')
    else:
        print('Discord 메시지 전송 성공')

    plot_comparison_results(user_stock_file_path1, user_stock_file_path2, stock, 'VOO', total_account_balance, total_rate, str_strategy, invested_amount, min_stock_data_date)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("대기중"))

@bot.command()
async def buddy(ctx):
    loop = asyncio.get_running_loop()

    for stock in stocks:
        await backtest_and_send(ctx, stock, 'modified_monthly')
        plot_results_mpl(stock, start_date, end_date)
        await asyncio.sleep(2)

    await loop.run_in_executor(None, update_stock_market_csv, 'stock_market.csv', stocks)
    sector_dict = await loop.run_in_executor(None, load_sector_info)
    path = '.'
    await loop.run_in_executor(None, merge_csv_files, path, sector_dict)

    await ctx.send("백테스팅 결과가 섹터별로 정리되었습니다.")

@bot.command()
async def ticker(ctx, *, query: str = None):
    print(f'Command received: ticker with query: {query}')
    if query is None:
        await ctx.send("ticker 주식명 or 티커를 입력하세요.")
        return

    ticker_dict = load_tickers()
    matching_tickers = search_tickers(query, ticker_dict)

    if not matching_tickers:
        await ctx.send("검색 결과가 없습니다.")
        return

    response_message = "검색 결과:\n"
    response_messages = []
    for symbol, name in matching_tickers:
        line = f"{symbol} - {name}\n"
        if len(response_message) + len(line) > 2000:
            response_messages.append(response_message)
            response_message = "검색 결과(계속):\n"
        response_message += line

    if response_message:
        response_messages.append(response_message)

    for message in response_messages:
        await ctx.send(message)
    print(f'Sent messages for query: {query}')

@bot.command()
async def stock(ctx, *args):
    stock_name = ' '.join(args)
    await ctx.send(f'명령어로 전달된 인자: {stock_name}')
    try:
        info_stock = str(stock_name).upper()  # 여기에 .upper()를 추가합니다.
        if info_stock.startswith('K '):  # 'stock k 흥국화재'
            korean_stock_name = info_stock[2:].upper()
            korean_stock_code = get_ticker_from_korean_name(korean_stock_name)  # 000540.KS,흥국화재,KOSPI
            if korean_stock_code is None:
                await ctx.send(f'{korean_stock_name} 주식을 찾을 수 없습니다.')
                return
            else:
                info_stock = korean_stock_code

        # 옵션에 따라 백테스트 및 결과 전송
        await backtest_and_send(ctx, info_stock, option_strategy='1')
        plot_results_mpl(info_stock, start_date, end_date)
    except Exception as e:  # Replace Exception with more specific exceptions if possible
        await ctx.send(f'An error occurred: {e}')

@bot.command()
async def show_all(ctx):
    try:
        await plot_results_all()
        await ctx.send("모든 결과가 성공적으로 표시되었습니다.")
    except Exception as e:
        await ctx.send(f"오류가 발생했습니다: {e}")
        print(f"오류: {e}")

bot.run(TOKEN)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))
# .\\.venv\\Scripts\\activate