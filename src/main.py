import asyncio

from src.configs.logger_setup import logger
from src.presentation.bot import bot, dp
from src.presentation.rest.routers import all_routers


for router in all_routers:
    dp.include_router(router)


async def start_bot():
    logger.info("Бот Запущен!!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())

