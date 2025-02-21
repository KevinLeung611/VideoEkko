import os
import sys
from urllib import parse

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ve.common import config

_BASE_URL = "https://api.siliconflow.cn"


def completions(system_prompt: str, user_prompt: str):
    api_key = config.get_config('gpt')['apiKey']
    model = config.get_config('gpt')['model']

    if not api_key:
        raise SystemExit("API key is not set! Check the conf.yaml file and add api key")

    if not model:
        raise SystemExit("Model is not set! Check the conf.yaml file and add model")

    api_path = "/v1/chat/completions"
    completions_url = parse.urljoin(_BASE_URL, api_path)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    }

    response = requests.post(completions_url, json=payload, headers=headers)
    return response.json()


if __name__ == '__main__':
    system_prompt = "你是一个专业的翻译器，请将下面的英文文本翻译成中文"
    user_prompt = "Creates a button, that when clicked, allows a user to download a single file of arbitrary type."
    print(completions(system_prompt, user_prompt))
