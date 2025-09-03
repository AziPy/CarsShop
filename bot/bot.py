import os
import django
from aiogram import Bot, Dispatcher
from decouple import config  # для чтения .env

# --- Подключаем Django ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from bot.handlers_user import register_user_handlers

# --- Читаем токен из .env ---
TOKEN = config("TELEGRAM_TOKEN")

# --- Создаём бота и диспетчер ---
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# --- Регистрируем хендлеры ---
register_user_handlers(dp)

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
