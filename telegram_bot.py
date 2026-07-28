import asyncio
import logging
import os
import functools
from functools import partial
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from google.cloud import dialogflow_v2 as dialogflow

logger = logging.getLogger(__name__)

def get_dialogflow_response(user_id: int, text: str, project_id: str, language_code: str) -> str:
    session_client = dialogflow.SessionsClient()
    session_id = str(user_id)
    session_path = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={"session": session_path, "query_input": query_input}
    )
    return response.query_result.fulfillment_text


async def start_command(message: types.Message):
    await message.answer("Здравствуйте")


async def handle_message(message: types.Message, bot: Bot, project_id: str, language_code: str):
    if message.text:
        try:
            answer = get_dialogflow_response(message.from_user.id, message.text,project_id, language_code)
            if not answer:
                answer = "Я вас не понимаю. Попробуйте переформулировать."
            await message.answer(answer)
        except Exception as e:
            logging.error(f"Ошибка при запросе к DialogFlow: {e}")
            await message.answer("Произошла ошибка при связи с сервером. Попробуйте позже.")


async def errors_handler(event: types.ErrorEvent, bot: Bot, admin_id: str):
    if admin_id:
        await bot.send_message(
            chat_id=admin_id, 
            text=f"Ошибка в Telegram боте:\n{event.exception}"
        )
    return True           


async def main():
    from dotenv import load_dotenv
    load_dotenv()

    bot_token = os.getenv("TELEGRAM_TOKEN_BOT")
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    language_code = "ru"
    admin_id = os.getenv("ADMIN_CHAT_ID")

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    bot = Bot(token=bot_token)
    dp = Dispatcher()

    dp.message.register(start_command, CommandStart())
    dp.message.register(functools.partial(
        handle_message,
        project_id=project_id,
        language_code=language_code)
    )
    dp.errors.register(
        functools.partial(errors_handler, admin_id=admin_id)
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())