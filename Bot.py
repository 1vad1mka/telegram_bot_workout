import asyncio
from aiogram import Bot, Dispatcher
from handlers_greeting import router as router_basic
from handlers_profile import  router as router_profile
from middleware import LoggingMiddleware
from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router_basic)
dp.include_router(router_profile)
dp.message.middleware(LoggingMiddleware())

# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
