"""VK bot with DialogFlow integration and monitoring."""

import os
import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from dialogflow_api import get_dialogflow_response


def send_error_to_tg(error_text: str, tg_token: str, admin_id: str):
    """Send error message to admin via Telegram."""
    if not tg_token or not admin_id:
        return
    url = f"https://api.telegram.org/bot{tg_token}/sendMessage"
    requests.post(
        url,
        json={
            "chat_id": admin_id,
            "text": f"Ошибка в VK боте:\n{error_text}",
        },
    )


def main():
    """Run the VK bot."""
    from dotenv import load_dotenv

    load_dotenv()

    vk_token = os.getenv("VK_GROUP_TOKEN")
    project_id = os.getenv("GOOGLE_PROJECT_ID")
    language_code = "ru"
    tg_token = os.getenv("TELEGRAM_TOKEN_BOT")
    admin_id = os.getenv("ADMIN_CHAT_ID")

    vk_session = vk_api.VkApi(token=vk_token)
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()

    print("VK Бот с DialogFlow запущен и слушает сообщения...")

    try:
        for event in longpoll.listen():
            if event.type != VkEventType.MESSAGE_NEW:
                continue

            if not event.to_me:
                continue

            print("Новое сообщение:")
            print("Для меня от: ", event.user_id)
            print("Текст:", event.text)

            try:
                answer, is_fallback = get_dialogflow_response(
                    event.user_id, event.text, project_id, language_code
                )
                if is_fallback:
                    print(
                        "Бот не понял фразу, пропускаем (оператор поможет)\n"
                    )
                    continue

                if answer:
                    vk.messages.send(
                        user_id=event.user_id, message=answer, random_id=0
                    )
                    print(f'Ответ отправлен: "{answer}"\n')
                else:
                    print("Пустой ответ от DialogFlow, пропускаем\n")
            except Exception as e:
                print(f"Ошибка при запросе к DialogFlow: {e}\n")
                send_error_to_tg(str(e), tg_token, admin_id)

    except Exception as e:
        print(f"Критическая ошибка Long Poll: {e}")
        send_error_to_tg(
            f"Критическая ошибка Long Poll: {e}", tg_token, admin_id
        )


if __name__ == "__main__":
    main()
