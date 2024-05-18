import openai
import os

# OpenAI GPT-3 API 키를 환경 변수에서 가져오거나 직접 지정합니다.
api_key = os.environ.get('chat_APIKEY')
if not api_key:
    api_key = 'chat_APIKEY'

def chat_with_gpt(prompt):
    # OpenAI GPT-3 API를 사용하여 대화하기
    response = openai.ChatCompletion.create(
        engine="text-davinci-002",  # GPT-3 엔진 선택
        prompt=prompt,  # 대화 시작
        max_tokens=50,  # 최대 토큰 수 설정 (상황에 맞게 조정)
        api_key=api_key
    )

    return response.choices[0].text.strip()
