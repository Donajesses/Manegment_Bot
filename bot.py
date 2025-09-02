import asyncio


from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from config import TOKEN
from app.handlers import router


dp = Dispatcher()
bot = Bot(token=TOKEN)


#апдейти бота
async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


#Точка входа в бота
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")