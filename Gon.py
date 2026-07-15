import discord
import requests
import os
import threading
from flask import Flask

# Discordのクライアント設定
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# 環境変数の読み込み
DIFY_API_KEY = os.environ.get('DIFY_API_KEY')
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')

@client.event
async def on_ready():
    print(f'ログインしました: {client.user}')

@client.event
async def on_message(message):
    # 1. Bot自身のメッセージは無視
    if message.author == client.user:
        return

    # 2. チャンネル制限（#ラウンジのみ）
    if message.channel.name != "ラウンジ":
        return

    # 3. ロール制限（メンバーロール保持者のみ）
    role_names = [role.name for role in message.author.roles]
    if "メンバー" not in role_names:
        return

    # 4. 反応する条件：
    #   A: メッセージに「ゴン」が含まれる
    #   B: メッセージが「ゴン（Bot）」への返信である
    is_reply_to_gon = False
    if message.reference and message.reference.resolved:
        if message.reference.resolved.author == client.user:
            is_reply_to_gon = True

    # 「ゴン」が含まれるか判定
    if "ゴン" in message.content or is_reply_to_gon:
        print("DEBUG: 「ゴン」という言葉を検知しました！")
        # ... (以下、Difyへの通信処理) ...
        api_url = "https://api.dify.ai/v1/chat-messages"
        headers = {"Authorization": f"Bearer {DIFY_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "inputs": {},
            "query": message.content,
            "response_mode": "blocking",
            "user": str(message.author.id)
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload)
            data = response.json()
            
            # ログにデバッグ情報を出す
            print(f"Dify Response: {data}")

            # 回答を取得
            reply = data.get("answer")
            if not reply:
                reply = "ごめん、うまく言葉にできないみたい。"
            
            await message.channel.send(reply)
            
        except Exception as e:
            print(f"エラー発生: {e}")
            await message.channel.send("通信エラーが発生しました。")

# Webサーバー（Render対策）
app = Flask(__name__)
@app.route('/')
def home():
    return "Gon is running!"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Webサーバーを別スレッドで起動
    threading.Thread(target=run_web, daemon=True).start()
    # Botの起動
    client.run(DISCORD_TOKEN)
