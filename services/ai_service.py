# services/ai_service.py

import openai
import logging

class AIAssistant:
    def __init__(self, api_key):
        openai.api_key = api_key

    def generate_response(self, user_query, context):
        try:
            messages = [
                {"role": "system", "content": context},
                {"role": "user", "content": user_query}
            ]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=400,
                temperature=0.7
            )
            return response.choices[0].message['content'].strip()
        except Exception as e:
            logging.error(f"Ошибка OpenAI: {e}")
            return None
