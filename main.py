import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
import database as db
from handlers import router
from middlewares import RateLimitMiddleware

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Initialize DB
    await db.create_tables()
    
    if not BOT_TOKEN:
        print("Ошибка: Токен бота не найден. Проверьте .env файл.")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    rate_limiter = RateLimitMiddleware()
    dp.message.middleware(rate_limiter)
    dp.callback_query.middleware(rate_limiter)

    print("Бот запущен...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен")
