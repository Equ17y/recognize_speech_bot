import os
from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

load_dotenv()
VK_TOKEN = os.getenv("VK_GROUP_TOKEN")

vk_session = vk_api.VkApi(token=VK_TOKEN)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

print("VK Эхо-бот запущен и слушает сообщения...")

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            print('Новое сообщение:')
            print('Для меня от: ', event.user_id)
            print('Текст:', event.text)
            
            vk.messages.send(
                user_id=event.user_id,
                message=event.text,
                random_id=0
            )
            print('Ответ отправлен\n')