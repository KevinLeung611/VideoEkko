import os
import sys
from urllib import parse

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ve.common import config

config = config.get_config('gpt')

_BASE_URL = "https://api.siliconflow.cn"
_API_KEY = config['apiKey']
_MODEL = config['model']

if not _API_KEY:
    raise SystemExit("API key is not set! Check the conf.yaml file and add api key")

if not _MODEL:
    raise SystemExit("Model is not set! Check the conf.yaml file and add model")

def completions(system_prompt: str, user_prompt: str):
    api_path = "/v1/chat/completions"
    completions_url = parse.urljoin(_BASE_URL, api_path)

    headers = {
        "Authorization": f"Bearer {_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": _MODEL,
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
