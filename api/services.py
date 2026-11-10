from openai import OpenAI
from django.conf import settings


def get_gpt_response(prompt):
    if settings.OPENAI_MOCK_MODE:
        return f"Тестовый ответ GPT на сообщение: {prompt}"

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    response = client.responses.create(
        model="gpt-5.5",
        input=prompt,
        max_output_tokens=300
    )

    return response.output_text