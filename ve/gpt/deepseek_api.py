import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from ve.gpt.open_api import OpenAPI

class DeepSeekAPI(OpenAPI):
    base_url = "https://api.deepseek.com"

    def __init__(self, model, api_key):
        super().__init__(model, api_key, self.base_url)
        self.api_key = api_key
        self.model = model

    def completions(self, system_prompt: str, user_prompt: str):
        return super().completions(system_prompt, user_prompt)


if __name__ == '__main__':
    from ve.common import config

    system_prompt = f"You are a Netflix subtitle translator. Please translate the following {'English'} sentence into {'Chinese'}. Do not provide any additional explanations, improvements, comments, notes or suggestions. Only provide the finally translation."
    user_prompt = "Well, here's an example from one of our smokers."
    api_key = config.get_config('gpt')['apiKey']
    model = config.get_config('gpt')['model']

    api = DeepSeekAPI(model, api_key)
    print(api.completions(system_prompt, user_prompt))
