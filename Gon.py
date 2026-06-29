import discord
import requests
import os

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

DIFY_API_KEY = os.environ.get('DIFY_API_KEY')
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

@client.event
async def on_ready():
    print(f'ログインしました: {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # ここから下が「ゴン」と呼んだ時の判定です
    if "ゴン" in message.content:
        api_url = "https://api.dify.ai/v1/chat-messages"
        headers = {"Authorization": f"Bearer {DIFY_API_KEY}"}
        payload = {
            "inputs": {},
            "query": message.content,
            "response_mode": "blocking",
            "conversation_id": "discord-user-" + str(message.author.id),
            "user": str(message.author.id)
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload)
            data = response.json()
            reply = data.get("answer", "ごめん、うまく返事ができないみたい。")
            await message.channel.send(reply)
        except Exception as e:
            print(f"エラー発生: {e}")
            await message.channel.send("通信エラーが発生しました。")

client.run(DISCORD_TOKEN)
