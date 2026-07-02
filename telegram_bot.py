import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from google.cloud import dialogflow_v2 as dialogflow

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN_BOT")
PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
LANGUAGE_CODE = "ru"

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def get_dialogflow_response(user_id: int, text: str) -> str:
    session_client = dialogflow.SessionsClient()
    session_id = str(user_id)
    session_path = session_client.session_path(PROJECT_ID, session_id)
    
    text_input = dialogflow.TextInput(text=text, language_code=LANGUAGE_CODE)
    query_input = dialogflow.QueryInput(text=text_input)
    
    response = session_client.detect_intent(
        request={"session": session_path, "query_input": query_input}
    )
    return response.query_result.fulfillment_text

@dp.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer("Здравствуйте")

@dp.message()
async def handle_message(message: types.Message):
    if message.text:
        try:
            answer = get_dialogflow_response(message.from_user.id, message.text)
            
            if not answer:
                answer = "Я вас не понимаю. Попробуйте переформулировать."
                
            await message.answer(answer)
            
        except Exception as e:
            logger.error(f"Ошибка при запросе к DialogFlow: {e}")
            await message.answer("Произошла ошибка при связи с сервером. Попробуйте позже.")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())