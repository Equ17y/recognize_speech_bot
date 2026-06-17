import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

load_dotenv()
TELEGRAM_TOKEN_BOT = os.getenv("TELEGRAM_TOKEN_BOT")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN_BOT)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer("Здравствуйте")


@dp.message()
async def handle_message(message: types.Message):
    if message.text:
        await message.answer(message.text)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())