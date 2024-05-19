from flask import Flask
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
from get_ticker import load_tickers, get_ticker_from_korean_name
from buy_stock import buy_us_stock, sell_us_stock
from estimate_stock import estimate_snp, estimate_stock
from get_account_balance import (
    calculate_buyable_balance,
    get_balance,
    get_market_from_ticker,
    get_ticker_price,
)
from get_earning import get_earning_alpha
from get_ranking import get_ranking_alpha
from Results_plot import plot_comparison_results, plot_results_all
from get_compare_stock_data import merge_csv_files, load_sector_info
from Results_plot_mpl import plot_results_mpl
import tracemalloc

load_dotenv()

app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

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
tickers = load_tickers()  # CSV 파일에서 티커 데이터 로드

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

key = os.getenv('H_APIKEY')
secret = os.getenv('H_SECRET')
acc_no = os.getenv('H_ACCOUNT')
ACC_NO_8 = os.getenv('H_ACCOUNT_8')

channel_id = os.getenv('DISCORD_CHANNEL_ID')

stocks = [
    'VOO', 'QQQ', 
    'NVDA', 'AMD'
]

    # 'AAPL', 'GOOGL', 'MSFT', 'U', 'SPOT', 'PLTR', 'ADBE', 'TSLA', 'APTV', 'FSLR', 'PFE', 'INMD', 'UNH',
    # 'TDOC', 'OXY', 'FSLR', 'ALB', 'AMZN', 'NFLX', 'LLY', 'EL', 'NKE', 'LOW', 'ADSK', 'NIO', 'F', 'BA', 'GE', 'JPM',
    # 'BAC', 'SQ', 'HD', 'PG', 'IONQ', '086520', 

start_date = "2022-01-01"
end_date = datetime.today().strftime('%Y-%m-%d')
initial_investment = 30000000
monthly_investment = 1000000

@bot.command()
async def buy(ctx, *args):
    buy_option = ' '.join(args)
    await ctx.send(f'명령어로 전달된 인자: {buy_option}')
    try:
        ticker, last_price, quantity = buy_option.split(',')
        ticker = ticker.strip().upper()
        market_info = get_market_from_ticker(ticker)
        last_price = get_ticker_price(key, secret, acc_no, market_info, ticker)
        last_price = round(float(last_price), 2)
        await ctx.send(f'주문단가: {last_price}')
        quantity = int(quantity.strip())
        resp = buy_us_stock(key, secret, acc_no, market_info, ticker, last_price, quantity)

        if 'msg_cd' in resp and resp['msg_cd'] == 'APBK0013':
            await ctx.send(f'{quantity}주의 {ticker}를 매수했습니다.')
        else:
            await ctx.send(f'주문에 실패했습니다. 오류 메시지: {resp["msg1"]}')
    except ValueError as e:
        await ctx.send(f'오류가 발생했습니다: {e}')
    except Exception as e:
        await ctx.send(f'알 수 없는 오류가 발생했습니다: {e}')

    await bot.change_presence(status=discord.Status.online, activity=discord.Game("대기중"))

@bot.command()
async def sell(ctx, *args):
    sell_option = ' '.join(args)
    await ctx.send(f'명령어로 전달된 인자: {sell_option}')
    try:
        ticker, last_price, quantity = sell_option.split(',')
        ticker = ticker.strip().upper()
        market_info = get_market_from_ticker(ticker)
        last_price = get_ticker_price(key, secret, acc_no, market_info, ticker)
        last_price = round(float(last_price), 2)
        await ctx.send(f'주문단가: {last_price}')
        quantity = int(quantity.strip())
        resp = sell_us_stock(key, secret, acc_no, market_info, ticker, last_price, quantity)

        if 'msg_cd' in resp and resp['msg_cd'] == 'APBK0013':
            await ctx.send(f'{quantity}주의 {ticker}를 매도했습니다.')
        else:
            if 'ordy' in resp['output'] and resp['output']['ordy'] == '매도불가':
                await ctx.send(f'{quantity}주의 {ticker}는 현재 주문 단가보다 높아 매도가 불가능합니다.')
            else:
                await ctx.send(f'주문에 실패했습니다. 오류 메시지: {resp["msg1"]}')
    except ValueError as e:
        await ctx.send(f'오류가 발생했습니다: {e}')
    except Exception as e:
        await ctx.send(f'알 수 없는 오류가 발생했습니다: {e}')

    await bot.change_presence(status=discord.Status.online, activity=discord.Game("대기중"))

@bot.command()
async def balance(ctx):
    global is_running
    is_running = True
    while is_running:
        DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
        won_psbl_amt, us_psbl_amt, frst_bltn_exrt, buyable_balance = calculate_buyable_balance(key, secret, acc_no)
        message = f'현재 매수가능금액은 {buyable_balance:.3f}$입니다.'
        response = requests.post(DISCORD_WEBHOOK_URL, data={'content': message})

        balance_data = get_balance(key, secret, acc_no)

        for item in balance_data:
            ticker = item['ticker']
            profit_amount = float(item.get('profit_amount', 0))
            my_quantity = float(item.get('holding_quantity', 0))
            average_price = float(item.get('average_price', 0))
            current_price = float(item.get('current_price', 0))
            my_rate = float(item.get('profit_rate', 0))
            name = item.get('name', '')

            message = {
                'content': (f"{ticker}({name})\n"
                            f"보유 수량 {my_quantity:.2f}, "
                            f"수익 금액 {profit_amount:.4f}, "
                            f"평균 가격 {average_price:.4f}, "
                            f"수익율 {my_rate:.4f}, "
                            f"현재 가격 {current_price:.4f} \n")
            }
            response = requests.post(DISCORD_WEBHOOK_URL, json=message)

            if response.status_code != 204:
                print(f'Discord 메시지 전송 실패: {ticker}')
            else:
                print(f'Discord 메시지 전송 성공: {ticker}')

            if my_rate < -3.0 and my_quantity > 1:
                sell_quantity = my_quantity // 2 if my_rate >= -5.0 else max(my_quantity - 1, 0)
                formatted_sell_quantity = f"{ticker},,{int(sell_quantity)}"
                await sell(ctx, formatted_sell_quantity)

            await asyncio.sleep(10)

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
async def ranking(ctx):
    try:
        result = get_ranking_alpha()
        DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
        message_content = f'```\n{result}\n```'
        data = {'content': message_content}
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)

        if response.status_code != 204:
            print('Discord 메시지 전송 실패')
        else:
            print('Discord 메시지 전송 성공')
    except Exception as e:
        await ctx.send(f"실행 중 오류 발생: {e}")

@bot.command()
async def earning(ctx, *args):
    stock_name = ' '.join(args)
    await ctx.send(f'명령어로 전달된 인자: {stock_name}')
    try:
        info_stock = str(stock_name).upper()
        result = get_earning_alpha(info_stock)

        DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')
        message_content = f'```\n{result}\n```'
        data = {'content': message_content}
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)

        if response.status_code != 204:
            print('Discord 메시지 전송 실패')
        else:
            print('Discord 메시지 전송 성공')
    except Exception as e:
        await ctx.send(f"실행 중 오류 발생: {e}")

@bot.command()
async def ticker(ctx, *, query: str = None):
    if query is None:
        await ctx.send("주식명을 입력해주세요.")
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

@bot.command()
async def stock(ctx, *args):
    stock_name = ' '.join(args)
    await ctx.send(f'명령어로 전달된 인자: {stock_name}')
    try:
        info_stock = str(stock_name).upper()
        if info_stock.startswith('K '):
            korean_stock_name = info_stock[2:].upper()
            korean_stock_code = get_ticker_from_korean_name(korean_stock_name)
            if korean_stock_code is None:
                await ctx.send(f'{korean_stock_name} 주식을 찾을 수 없습니다.')
                return
            else:
                info_stock = korean_stock_code

        await ctx.send(
            "백테스팅 옵션을 선택해주세요:\n"
            "1: 디폴트 옵션\n"
            "2: 적립식 투자\n"
            "3: 변형 적립식투자(이익금 안정화)"
        )

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content in ['1', '2', '3']

        try:
            option_msg = await bot.wait_for('message', check=check, timeout=5.0)
            option = option_msg.content
        except asyncio.TimeoutError:
            option = '3'
            await ctx.send("시간 초과: 변형 적립식투자(이익금 안정화) 옵션을 자동으로 선택합니다.")

        if option not in ['1', '2', '3']:
            await ctx.send("잘못된 옵션입니다. 1, 2, 또는 3 중에서 선택해주세요.")
            return

        option_strategy = 'default' if option == '1' else 'monthly' if option == '2' else 'modified_monthly'
        option_text = '디폴트 옵션' if option == '1' else '적립식 투자' if option == '2' else '변형 적립식투자'
        await ctx.send(f"{stock_name} 주식을 {option_text}으로 검토하겠습니다.")

        await backtest_and_send(ctx, info_stock, option_strategy)
        plot_results_mpl(info_stock, start_date, end_date)
    except Exception as e:
        await ctx.send(f'An error occurred: {e}')
    stock_name = ' '.join(args).strip()
    await ctx.send(f'명령어로 전달된 인자: {stock_name}')
    try:
        info_stock = str(stock_name).upper()
        if info_stock.startswith('K '):
            korean_stock_name = info_stock[2:].strip()
            korean_stock_code = get_ticker_from_korean_name(korean_stock_name, tickers)
            if korean_stock_code is None:
                await ctx.send(f'{korean_stock_name} 주식을 찾을 수 없습니다.')
                return
            else:
                info_stock = korean_stock_code

        await ctx.send(
            "백테스팅 옵션을 선택해주세요:\n"
            "1: 디폴트 옵션\n"
            "2: 적립식 투자\n"
            "3: 변형 적립식투자(이익금 안정화)"
        )

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel and m.content in ['1', '2', '3']

        try:
            option_msg = await bot.wait_for('message', check=check, timeout=30.0)
            option = option_msg.content
        except asyncio.TimeoutError:
            option = '3'
            await ctx.send("시간 초과: 변형 적립식투자(이익금 안정화) 옵션을 자동으로 선택합니다.")

        if option not in ['1', '2', '3']:
            await ctx.send("잘못된 옵션입니다. 1, 2, 또는 3 중에서 선택해주세요.")
            return

        option_strategy = 'default' if option == '1' else 'monthly' if option == '2' else 'modified_monthly'
        option_text = '디폴트 옵션' if option == '1' else '적립식 투자' if option == '2' else '변형 적립식투자'
        await ctx.send(f"{stock_name} 주식을 {option_text}으로 검토하겠습니다.")

        await backtest_and_send(ctx, info_stock, option_strategy)
        plot_results_mpl(info_stock, start_date, end_date)
    except Exception as e:
        await ctx.send(f'An error occurred: {e}')


@bot.command()
async def show_all(ctx):
    try:
        await plot_results_all()
        await ctx.send("모든 결과가 성공적으로 표시되었습니다.")
    except Exception as e:
        await ctx.send(f"오류가 발생했습니다: {e}")
        print(f"오류: {e}")

@bot.command()
async def stream(ctx, *args):
    stream_option = ' '.join(args)
    await ctx.send(f'명령어로 전달된 인자: {stream_option}')
    try:
        ticker, quantity = stream_option.split(',')
        ticker = ticker.strip().upper()
        market_info = get_market_from_ticker(ticker)
        last_price = get_ticker_price(key, secret, acc_no, market_info, ticker)
        last_price = round(float(last_price), 2)
        await ctx.send(f'현재가: {last_price}')
        quantity = int(quantity.strip())
        resp = sell_us_stock(key, secret, acc_no, market_info, ticker, last_price, quantity)

        if 'msg_cd' in resp and resp['msg_cd'] == 'APBK0013':
            await ctx.send(f'{quantity}주의 {ticker}를 매도했습니다.')
        else:
            if 'ordy' in resp['output'] and resp['output']['ordy'] == '매도불가':
                await ctx.send(f'{quantity}주의 {ticker}는 현재 주문 단가보다 높아 매도가 불가능합니다.')
            else:
                await ctx.send(f'주문에 실패했습니다. 오류 메시지: {resp["msg1"]}')
    except ValueError as e:
        await ctx.send(f'오류가 발생했습니다: {e}')
    except Exception as e:
        await ctx.send(f'알 수 없는 오류가 발생했습니다: {e}')

    await bot.change_presence(status=discord.Status.online, activity=discord.Game("대기중"))

bot.run(TOKEN)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))
# .\\myenv\\Scripts\\activate
