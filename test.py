from flask import Flask
from threading import Thread
import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

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
intents.message_content = True  # Add this line to enable message content intent

bot = commands.Bot(command_prefix='!', intents=intents)

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

bot.run(TOKEN)


# .\\myenv\\Scripts\\activate
