# main.py
    # 'AAPL', 'GOOGL', 'MSFT', 'U', 'SPOT', 'PLTR', 'ADBE', 'TSLA', 'APTV', 'FSLR', 'PFE', 'INMD', 'UNH',
    # 'TDOC', 'OXY', 'FSLR', 'ALB', 'AMZN', 'NFLX', 'LLY', 'EL', 'NKE', 'LOW', 'ADSK', 'NIO', 'F', 'BA', 'GE', 'JPM',
    # 'BAC', 'SQ', 'HD', 'PG', 'IONQ', '086520', 

from flask import Flask, request, jsonify, Response
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
from get_ticker import load_tickers, search_tickers, get_ticker_name, update_stock_market_csv
from estimate_stock import estimate_snp, estimate_stock
from Results_plot import plot_comparison_results, plot_results_all
from get_compare_stock_data import merge_csv_files, load_sector_info
from Results_plot_mpl import plot_results_mpl
import tracemalloc
from flask_cors import CORS
import xml.etree.ElementTree as ET

load_dotenv()

app = Flask('')
CORS(app)

@app.route('/')
def home():
    return "I'm alive"

@app.route('/save_search_history', methods=['POST'])
def save_search_history():
    data = request.json
    stock_name = data.get('stock_name')
    if not stock_name:
        return jsonify(success=False, error="No stock name provided"), 400

    log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {stock_name}\n"

    # 로컬 파일에 로그 저장
    try:
        with open('search_history.log', 'a') as log_file:
            log_file.write(log_entry)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

    # Discord 웹훅에 로그 전송
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if webhook_url:
        payload = {
            "content": log_entry
        }
        try:
            response = requests.post(webhook_url, json=payload)
            if response.status_code != 204:
                return jsonify(success=False, error="Failed to send to Discord"), 500
        except Exception as e:
            return jsonify(success=False, error=str(e)), 500

    return jsonify(success=True)

@app.route('/api/get_tickers', methods=['GET'])
def get_tickers():
    try:
        stock_data = pd.read_csv('stock_market.csv')
        tickers = stock_data[['Symbol', 'Name', 'Market', 'Sector', 'Industry']].dropna().to_dict(orient='records')
        return jsonify(tickers)
    except Exception as e:
        return jsonify(error=str(e)), 500

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
    print(f'Bot has successfully logged in: {bot.user.name}')
    channel = bot.get_channel(int(CHANNEL_ID))
    if channel:
        await channel.send(f'Bot has successfully logged in: {bot.user.name}')
    else:
        print(f"Cannot find the channel: {CHANNEL_ID}")

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
        print('Failed to send Discord message')
    else:
        print('Successfully sent Discord message')

    plot_comparison_results(user_stock_file_path1, user_stock_file_path2, stock, 'VOO', total_account_balance, total_rate, str_strategy, invested_amount, min_stock_data_date)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("Waiting"))

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

    await ctx.send("Backtesting results have been organized by sector.")

@bot.command()
async def ticker(ctx, *, query: str = None):
    print(f'Command received: ticker with query: {query}')
    if query is None:
        await ctx.send("Please enter ticker stock name or ticker.")
        return

    ticker_dict = load_tickers()
    matching_tickers = search_tickers(query, ticker_dict)

    if not matching_tickers:
        await ctx.send("No search results.")
        return

    response_message = "Search results:\n"
    response_messages = []
    for symbol, name in matching_tickers:
        line = f"{symbol} - {name}\n"
        if len(response_message) + len(line) > 2000:
            response_messages.append(response_message)
            response_message = "Search results (continued):\n"
        response_message += line

    if response_message:
        response_messages.append(response_message)

    for message in response_messages:
        await ctx.send(message)
    print(f'Sent messages for query: {query}')

@bot.command()
async def stock(ctx, *args):
    stock_name = ' '.join(args)
    await ctx.send(f'Arguments passed by command: {stock_name}')
    try:
        info_stock = str(stock_name).upper()  # Add .upper() here
        if info_stock.startswith('K '):  # 'stock k Heungkuk Fire & Marine Insurance'
            korean_stock_name = info_stock[2:].upper()
            korean_stock_code = get_ticker_from_korean_name(korean_stock_name)  # 000540.KS,Heungkuk Fire & Marine Insurance,KOSPI
            if korean_stock_code is None:
                await ctx.send(f'Cannot find the stock {korean_stock_name}.')
                return
            else:
                info_stock = korean_stock_code

        # Backtest and send results depending on the option
        await backtest_and_send(ctx, info_stock, option_strategy='1')
        plot_results_mpl(info_stock, start_date, end_date)
    except Exception as e:  # Replace Exception with more specific exceptions if possible
        await ctx.send(f'An error occurred: {e}')

@bot.command()
async def show_all(ctx):
    try:
        await plot_results_all()
        await ctx.send("All results have been successfully displayed.")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")
        print(f"Error: {e}")

bot.run(TOKEN)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))

# .\\.venv\\Scripts\\activate
# python main.py