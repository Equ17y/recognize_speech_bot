"""Script to create DialogFlow intents from JSON file."""

import os
import json
from google.cloud import dialogflow_v2 as dialogflow


def create_intents_from_json(json_file_path: str, project_id: str) -> list:
    """Create intents in DialogFlow from JSON. Returns list of results."""
    with open(json_file_path, "r", encoding="utf-8") as f:
        raw_intents = json.load(f)

    intents_client = dialogflow.IntentsClient()
    parent = f"projects/{project_id}/agent"
    creation_report = []

    for intent_name, intent_data in raw_intents.items():
        clean_intent_name = intent_name.strip()
        questions_key = next(
            (k for k in intent_data.keys() if k.strip() == "questions"), None
        )
        answer_key = next(
            (k for k in intent_data.keys() if k.strip() == "answer"), None
        )

        if not questions_key or not answer_key:
            creation_report.append(
                {
                    "name": clean_intent_name,
                    "status": "error",
                    "message": "Не найдены ключи",
                }
            )
            continue

        questions = intent_data[questions_key]
        answer = intent_data[answer_key].strip()

        training_phrases = []
        for question in questions:
            part = dialogflow.Intent.TrainingPhrase.Part(
                text=question.strip()
            )
            training_phrase = dialogflow.Intent.TrainingPhrase(parts=[part])
            training_phrases.append(training_phrase)

        text_message = dialogflow.Intent.Message.Text(text=[answer])
        message = dialogflow.Intent.Message(text=text_message)

        intent = dialogflow.Intent(
            display_name=clean_intent_name,
            training_phrases=training_phrases,
            messages=[message],
        )

        try:
            response = intents_client.create_intent(
                parent=parent, intent=intent
            )
            creation_report.append(
                {
                    "name": response.display_name,
                    "status": "ok",
                    "phrases": len(response.training_phrases),
                }
            )
        except Exception as e:
            creation_report.append(
                {
                    "name": clean_intent_name,
                    "status": "error",
                    "message": str(e),
                }
            )
    return creation_report


def main():
    """Load env, create intents and print results."""
    from dotenv import load_dotenv

    load_dotenv()

    project_id = os.getenv("GOOGLE_PROJECT_ID")

    creation_report = create_intents_from_json("learning_offers.json", project_id)

    for result in creation_report:
        if result["status"] == "ok":
            print(f"Создан: '{result['name']}' (фраз: {result['phrases']})")
        else:
            print(
                f"Ошибка для '{result['name']}': "
                f"{result.get('message','Не найдены ключи')}"
            )
        print("-" * 50)


if __name__ == "__main__":
    main()
