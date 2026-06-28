import discord
from discord.ext import commands
import aiohttp
import os
from dotenv import load_dotenv

# ...この下に設定などが続きます...

# ----------------- 設定項目 -----------------
# .envファイルの内容を読み込む
load_dotenv()

# os.getenv() を使って環境変数（.env）から値を取得する
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("エラー: .env に DISCORD_TOKEN が設定されていません。")

DIFY_API_KEY = os.getenv("DIFY_API_KEY")
if not DIFY_API_KEY:
    raise ValueError("エラー: .env に DIFY_API_KEY が設定されていません。")

DIFY_API_URL = "https://api.dify.ai/v1/chat-messages"
# --------------------------------------------

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 会話履歴を保持するための辞書
conversations = {}
# 重複処理を防ぐためのセット
processing_messages = set()

@bot.event
async def on_ready():
    print(f"{bot.user} としてログインしました")

@bot.event
async def on_message(message):
    # 1. 自分を含む「すべてのBot」の発言を完全に無視する
    if message.author.bot:
        return

    # 2. すでに処理中のメッセージなら無視（連投防止）
    if message.id in processing_messages:
        return
    
    # 3. 処理開始のマーク
    processing_messages.add(message.id)

    try:
        user_id = str(message.author.id)
        conversation_id = conversations.get(user_id, "")

        headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": {},
            "query": message.content,
            "response_mode": "blocking",
            "user": user_id,
            "conversation_id": conversation_id
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(DIFY_API_URL, json=payload, headers=headers) as response:
                
                # エラー発生時の処理（400系や500系エラー）
                if response.status != 200:
                    await message.channel.send("ゴンが少しお休み中です…（APIエラー）")
                    print(f"Error: {response.status}, {await response.text()}")
                    return # 処理を中断

                data = await response.json()
                answer = data.get("answer", "")
                
                # 会話IDの更新
                if "conversation_id" in data:
                    conversations[user_id] = data["conversation_id"]
                
                # 返信の送信
                if answer:
                    await message.channel.send(answer)

    except Exception as e:
        print(f"予期せぬエラー: {e}")
    
    finally:
        # 処理が終わったらリストからIDを削除
        processing_messages.discard(message.id)

bot.run(DISCORD_TOKEN)