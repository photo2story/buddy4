import os
import discord
from discord.ext import commands

# 환경변수에서 토큰 및 채널 ID 가져오기
TOKEN = os.getenv('DISCORD_APPLICATION_TOKEN')
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

# 디스코드 봇 인텐트 설정
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# 봇 객체 생성
bot = commands.Bot(command_prefix='', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot이 성공적으로 로그인했습니다: {bot.user.name}')
    print(f'Bot is ready to receive commands.')

# 상태를 저장할 변수
awaiting_ticker = False

@bot.command(name='ticker')
async def ticker(ctx, *, query: str = None):
    global awaiting_ticker
    if query is None:
        awaiting_ticker = True
        await ctx.send("주식명을 입력해주세요.")
        print('Awaiting ticker name...')
    else:
        awaiting_ticker = False
        print(f'Command received: ticker with query: {query}')
        await ctx.send(f'검색된 주식명: {query}')
        print(f'Sent messages for query: {query}')

@bot.event
async def on_message(message):
    global awaiting_ticker
    if awaiting_ticker and message.content:
        ctx = await bot.get_context(message)
        if ctx.valid:
            awaiting_ticker = False
            await ticker(ctx, query=message.content)
        return
    await bot.process_commands(message)

bot.run(TOKEN)
