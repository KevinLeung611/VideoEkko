import json.decoder

import openai


class OpenAPI:

    def __init__(self, model: str, api_key: str, base_url: str = None):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key

    def completions(self, system_prompt: str, user_prompt: str):
        try:
            api_key = self.api_key
            model = self.model
            client = openai.OpenAI(api_key=api_key, base_url=self.base_url)
            messages = [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
            response = client.chat.completions.create(model=model, stream=False, messages=messages)
            return response.choices[0].message.content
        except openai.OpenAIError as e:
            print(f"Request an open api failed: {e}, api url: {self.base_url}")
            raise e
        except json.decoder.JSONDecodeError as e:
            print(f"AI Server response failed! Please check the logs.")


if __name__ == '__main__':
    from ve.common import config

    system_prompt = f"You are a Netflix subtitle translator. Please translate the following {'English'} sentence into {'Chinese'}. Do not provide any additional explanations, improvements, comments, notes or suggestions. Only provide the finally translation."
    user_prompt = "Well, here's an example from one of our smokers."

    api_key = config.get_config('gpt')['apiKey']
    model = config.get_config('gpt')['model']

    api = OpenAPI(model, api_key)
    print(api.completions(system_prompt, user_prompt))
