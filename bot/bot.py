import os
import sys
import django
import asyncio
from decouple import config
from aiogram import Bot, Dispatcher

# --- Настройка пути ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# --- Настройка Django ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()  # <- обязательно до любых импортов моделей!

# Импортируем router, а не register_user_handlers!
from bot.handlers_user import router

# --- Telegram token ---
TOKEN = config("TELEGRAM_TOKEN")

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    # ✅ Подключаем router
    dp.include_router(router)

    print("🤖 Бот запущен и слушает команды...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
