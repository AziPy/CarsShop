import os
import sys
import django
import asyncio
from decouple import config
from aiogram import Bot, Dispatcher

if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, BASE_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
    django.setup()

# ================== Import Router AFTER Django Setup ==================
from bot_app.handlers_user import router
TOKEN = config("TELEGRAM_TOKEN")


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    dp.include_router(router)

    print("🤖 Бот запущен и слушает команды...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        import uvloop
        uvloop.install()
        print("✅ Используется uvloop для улучшенной производительности")
    except ImportError:
        print("⚠️  uvloop не установлен. Используется стандартный asyncio")

    asyncio.run(main())