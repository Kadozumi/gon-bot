import discord
from discord.ext import commands
import aiohttp
import os
import asyncio
from dotenv import load_dotenv
from aiohttp import web

# 環境変数の読み込み
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
DIFY_API_KEY = os.getenv("DIFY_API_KEY")
DIFY_API_URL = "https://api.dify.ai/v1/chat-messages"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

conversations = {}
processing_messages = set()

# --- 追加部分：Webサーバー機能 ---
async def handle(request):
    return web.Response(text="Gon is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 8080)))
    await site.start()

# --- Discord Botの処理 ---
@bot.event
async def on_ready():
    print(f"{bot.user} としてログインしました")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.id in processing_messages:
        return
    processing_messages.add(message.id)

    try:
        user_id = str(message.author.id)
        conversation_id = conversations.get(user_id, "")
        headers = {"Authorization": f"Bearer {DIFY_API_KEY}", "Content-Type": "application/json"}
        payload = {"inputs": {}, "query": message.content, "response_mode": "blocking", "user": user_id, "conversation_id": conversation_id}

        async with aiohttp.ClientSession() as session:
            async with session.post(DIFY_API_URL, json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    answer = data.get("answer", "")
                    if "conversation_id" in data:
                        conversations[user_id] = data["conversation_id"]
                    if answer:
                        await message.channel.send(answer)
    finally:
        processing_messages.discard(message.id)

# --- 起動処理 ---
async def main():
    await asyncio.gather(bot.start(TOKEN), start_web_server())

if __name__ == "__main__":
    asyncio.run(main())
