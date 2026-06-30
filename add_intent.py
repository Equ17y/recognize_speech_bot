import os
import json
from dotenv import load_dotenv
from google.cloud import dialogflow_v2 as dialogflow

load_dotenv()
PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")

def create_intents_from_json(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    intents_client = dialogflow.IntentsClient()
    
    parent = f"projects/{PROJECT_ID}/agent"

    for intent_name, intent_data in data.items():
        clean_intent_name = intent_name.strip()
        
        # Ищем ключи, игнорируя пробелы
        questions_key = next((k for k in intent_data.keys() if k.strip() == "questions"), None)
        answer_key = next((k for k in intent_data.keys() if k.strip() == "answer"), None)
        
        if not questions_key or not answer_key:
            print(f"Не найдены ключи в '{clean_intent_name}'")
            continue
        
        questions = intent_data[questions_key]
        answer = intent_data[answer_key].strip()

        # Формируем фразы
        training_phrases = []
        for question in questions:
            part = dialogflow.Intent.TrainingPhrase.Part(text=question.strip())
            training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
            training_phrases.append(training_phrase)

        # Формируем ответ
        text_message = dialogflow.Intent.Message.Text(text=[answer])
        message = dialogflow.Intent.Message(text=text_message)

        intent = dialogflow.Intent(
            display_name=clean_intent_name,
            training_phrases=training_phrases,
            messages=[message]
        )

        print(f"Создаём интент: '{clean_intent_name}'...")
        print(f"Количество фраз для отправки: {len(training_phrases)}")
        
        try:
            response = intents_client.create_intent(parent=parent, intent=intent)
            print(f"Создан: '{response.display_name}' (фраз: {len(response.training_phrases)})")
        except Exception as e:
            print(f"Ошибка при создании '{clean_intent_name}': {e}")
        
        print("-" * 50)

if __name__ == "__main__":
    create_intents_from_json("learning_offers.json")