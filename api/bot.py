import asyncio
import os
import redis
from telegram import Update
from telegram.ext import Application, MessageHandler, filters
from lib.coach import handle_message

async def handler(request):
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    kv_url = os.getenv('KV_URL')

    application = Application.builder().token(bot_token).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # تنظیم webhook اگر تنظیم نشده
    kv = redis.from_url(kv_url)
    if not kv.get("webhook_set"):
        host = request.headers.get('host', 'localhost')
        url = f"https://{host}/api/bot"
        await application.bot.set_webhook(url=url)
        kv.set("webhook_set", "1")

    # پردازش به‌روزرسانی
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)

    return {"status": "ok"}