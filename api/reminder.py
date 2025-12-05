import os
import redis
from telegram import Bot

async def handler(request):
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    kv_url = os.getenv('KV_URL')

    bot = Bot(token=bot_token)
    kv = redis.from_url(kv_url)
    users = kv.smembers("users")

    for user_id_bytes in users:
        user_id = int(user_id_bytes.decode())
        try:
            await bot.send_message(chat_id=user_id, text="یادآوری روزانه: به یادگیری پایتون ادامه دهید و مراحل را کامل کنید!")
        except Exception as e:
            print(f"Error sending to {user_id}: {e}")

    return {"status": "ok"}