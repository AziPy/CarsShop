import os
import sys
import django

# --- Гарантируем, что корень проекта в sys.path ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# --- Указываем Django, где искать настройки ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

# --- Теперь можно тянуть всё остальное ---
from aiogram import Bot, Dispatcher
from decouple import config
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
