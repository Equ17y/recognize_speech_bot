"""Module for working with DialogFlow API."""
from google.cloud import dialogflow_v2 as dialogflow


def get_dialogflow_response(
    user_id: int, text: str, project_id: str, language_code: str
):
    """Send text to DialogFlow and return (response, is_fallback)."""
    session_client = dialogflow.SessionsClient()
    session_id = str(user_id)
    session_path = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(
        request={"session": session_path, "query_input": query_input}
    )

    is_fallback = (
        response.query_result.intent.is_fallback
        if response.query_result.intent
        else True
    )
    return response.query_result.fulfillment_text, is_fallback