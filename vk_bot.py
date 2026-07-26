import os
import requests
from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from google.cloud import dialogflow_v2 as dialogflow

load_dotenv()
VK_TOKEN = os.getenv("VK_GROUP_TOKEN")
PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
LANGUAGE_CODE = "ru"

TG_BOT_TOKEN = os.getenv("TELEGRAM_TOKEN_BOT")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

def send_error_to_tg(error_text):
    if not TG_BOT_TOKEN or not ADMIN_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            "chat_id": ADMIN_CHAT_ID,
            "text": f"Ошибка в VK боте:\n{error_text}"
        })
    except Exception as e:
        print(f"Не удалось отправить ошибку в Telegram: {e}")

vk_session = vk_api.VkApi(token=VK_TOKEN)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

def get_dialogflow_response(user_id: int, text: str):
    session_client = dialogflow.SessionsClient()
    session_id = str(user_id)
    session_path = session_client.session_path(PROJECT_ID, session_id)
    
    text_input = dialogflow.TextInput(text=text, language_code=LANGUAGE_CODE)
    query_input = dialogflow.QueryInput(text=text_input)
    
    response = session_client.detect_intent(
        request={"session": session_path, "query_input": query_input}
    )
    
    is_fallback = response.query_result.intent.is_fallback if response.query_result.intent else True
    
    return response.query_result.fulfillment_text, is_fallback

print("VK Бот с DialogFlow запущен и слушает сообщения...")

try:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                print('Новое сообщение:')
                print('Для меня от: ', event.user_id)
                print('Текст:', event.text)
                
                try:
                    answer, is_fallback = get_dialogflow_response(event.user_id, event.text)
                    
                    if is_fallback:
                        print('Бот не понял фразу, пропускаем (оператор поможет)\n')
                        continue
                    
                    if answer:
                        vk.messages.send(
                            user_id=event.user_id,
                            message=answer,
                            random_id=0
                        )
                        print(f'Ответ отправлен: "{answer}"\n')
                    else:
                        print('Пустой ответ от DialogFlow, пропускаем\n')
                except Exception as e:
                    print(f'Ошибка при запросе к DialogFlow: {e}\n')
                    send_error_to_tg(str(e))
                    
except Exception as e:
    print(f'Ошибка при запросе к DialogFlow: {e}\n')
    send_error_to_tg(f"Критическая ошибка Long Poll: {e}")