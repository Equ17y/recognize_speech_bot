"""Telegram bot with DialogFlow integration."""

import asyncio
import logging
import os
from functools import partial
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from dialogflow_api import get_dialogflow_response

logger = logging.getLogger(__name__)


async def start_command(message: types.Message):
    """Handle /start command."""
    await message.answer("Здравствуйте")


async def handle_message(
    message: types.Message, bot: Bot, project_id: str, language_code: str
):
    """Handle text messages and send them to DialogFlow."""
    if message.text:
        try:
            answer, _ = get_dialogflow_response(
                message.from_user.id, message.text, project_id, language_code
            )
            if not answer:
                answer = "Я вас не понимаю. Попробуйте переформулировать."
            await message.answer(answer)
        except Exception as e:
            logging.error(f"Ошибка при запросе к DialogFlow: {e}")
            await message.answer(
                "Произошла ошибка при связи с сервером. Попробуйте позже."
            )


async def errors_handler(event: types.ErrorEvent, bot: Bot, admin_id: str):
    """Send errors to admin via Telegram."""
    if admin_id:
        await bot.send_message(
            chat_id=admin_id,
            text=f"Ошибка в Telegram боте:\n{event.exception}",
        )
    return True


async def main():
    """Run the Telegram bot."""
    from dotenv import load_dotenv

    load_dotenv()

    bot_token = os.getenv("TELEGRAM_TOKEN_BOT")
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    language_code = "ru"
    admin_id = os.getenv("ADMIN_CHAT_ID")

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    bot = Bot(token=bot_token)
    dp = Dispatcher()

    dp.message.register(start_command, CommandStart())
    dp.message.register(
        partial(
            handle_message, project_id=project_id, language_code=language_code
        )
    )
    dp.errors.register(partial(errors_handler, admin_id=admin_id))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
