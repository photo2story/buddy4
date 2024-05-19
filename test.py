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
intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot이 성공적으로 로그인했습니다: {bot.user.name}')

@bot.command()
async def ping(ctx):
    await ctx.send(f'pong: {bot.user.name}')

bot.run(TOKEN)
