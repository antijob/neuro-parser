import openai
from django.conf import settings

openai.api_key = settings.CHAT_GPT_KEY

def predict_is_incident(text, prompt, positive_result):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": ""},
            {"role": "assistant", "content": text},
        ],
    )

    result = response['choices'][0]['message']['content']

    # postprocess rules
    if result.endswith('.'):
        result = result[:-1]

    # May be look if result contains positive_result?
    return ( result == positive_result )