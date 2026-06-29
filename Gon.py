import discord
import requests
import os

# Discordのクライアント設定
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 環境変数からAPIキーなどを取得
DIFY_API_KEY = os.environ.get('DIFY_API_KEY')
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

@client.event
async def on_ready():
    print(f'ログインしました: {client.user}')

@client.event
async def on_message(message):
    # 1. ゴン自身の発言には反応しない（無限ループ防止）
    if message.author == client.user:
        return

    # 2. メッセージの中に「ゴン」という名前が含まれているか確認
    if "ゴン" in message.content:
        
        # Difyへ送信する処理
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

# ボットの起動
client.run(DISCORD_TOKEN)
