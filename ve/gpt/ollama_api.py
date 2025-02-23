from urllib import parse
from openai import OpenAIError

import requests


class OllamaAPI:

    def __init__(self,
                 model: str,
                 base_url: str = "http://localhost",
                 port: int = 11434):
        self.model = model
        self.base_url = base_url
        self.port = port

    def set_port(self, port):
        self.port = port

    def completions(self, system_prompt: str, user_prompt: str):
        api_path = "/api/chat"

        messages = [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "format": "json"
        }

        url = parse.urljoin(f"{self.base_url}:{self.port}", api_path)

        response = requests.post(url, json=payload)

        if response.status_code != requests.codes.ok:
            raise OpenAIError(response.status_code, response.text)

        return response.json()['message']['content']


if __name__ == '__main__':
    from ve.common import config

    system_prompt = f"You are a Netflix subtitle translator. Please translate the following {'English'} sentence into {'Chinese'}. Do not provide any additional explanations, improvements, comments, notes or suggestions. Only provide the finally translation."
    user_prompt = "Well, here's an example from one of our smokers."

    model = config.get_config('gpt')['model']
    api = OllamaAPI(model)
    print(api.completions(system_prompt, user_prompt))
