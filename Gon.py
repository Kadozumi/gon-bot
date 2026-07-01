import discord
import requests
import os
import threading
from flask import Flask

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
            # ここを追加：Difyからの応答内容をログに出力する
            print(f"Dify Response Status: {response.status_code}")
            print(f"Dify Response Data: {response.text}")
            
            data = response.json()
            reply = data.get("answer", "ごめん、答えが見つからなかったよ。")
            await message.channel.send(reply)
        except Exception as e:
            # ここでエラーの詳細をログに出す
            print(f"詳細エラー: {e}")
            await message.channel.send("通信エラーが発生しました。")

# ダミーのWebサーバーを立てる（Render対策）
app = Flask(__name__)
@app.route('/')
def home():
    return "Gon is running!"

def run_web():
    # Renderが指定するポート番号を取得（デフォルトは10000）
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

# Webサーバーを別スレッドで起動
threading.Thread(target=run_web).start()

# Botの起動
client.run(DISCORD_TOKEN)
