import os
from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from google.cloud import dialogflow_v2 as dialogflow

load_dotenv()
VK_TOKEN = os.getenv("VK_GROUP_TOKEN")
PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
LANGUAGE_CODE = "ru"

vk_session = vk_api.VkApi(token=VK_TOKEN)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()


def get_dialogflow_response(user_id: int, text: str) -> str:
    """Отправляет текст пользователя в DialogFlow и возвращает ответ."""
    session_client = dialogflow.SessionsClient()
    session_id = str(user_id)
    session_path = session_client.session_path(PROJECT_ID, session_id)
    
    text_input = dialogflow.TextInput(text=text, language_code=LANGUAGE_CODE)
    query_input = dialogflow.QueryInput(text=text_input)
    
    response = session_client.detect_intent(
        request={"session": session_path, "query_input": query_input}
    )
    return response.query_result.fulfillment_text

print("VK Бот с DialogFlow запущен и слушает сообщения...")


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            print('Новое сообщение:')
            print('Для меня от: ', event.user_id)
            print('Текст:', event.text)
            
            try:
                answer = get_dialogflow_response(event.user_id, event.text)
                
                if not answer:
                    answer = "Я вас не понимаю. Попробуйте переформулировать."
                
                vk.messages.send(
                    user_id=event.user_id,
                    message=answer,
                    random_id=0
                )
                print(f'Ответ отправлен: "{answer}"\n')
                
            except Exception as e:
                print(f'Ошибка при запросе к DialogFlow: {e}')
                vk.messages.send(
                    user_id=event.user_id,
                    message="Произошла ошибка при связи с сервером. Попробуйте позже.",
                    random_id=0
                )