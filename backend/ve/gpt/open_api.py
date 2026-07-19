import json.decoder
import logging
import time
import openai

logger = logging.getLogger(__name__)

class OpenAPI:

    def __init__(self, model: str, api_key: str, base_url: str = None):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key

    def completions(self, system_prompt: str, user_prompt: str):
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

        i = 0
        retry_times = 3
        while i < retry_times:
            try:
                response = client.chat.completions.create(model=model, stream=False, messages=messages)
                return response.choices[0].message.content
            except (openai.RateLimitError, openai.APIConnectionError, openai.APITimeoutError) as e:
                logger.exception(f"Rate limit error. url: {self.base_url}, Retry: {i}")
                time.sleep(3)
                i += 1
                continue
            except openai.APIStatusError as e:
                if e.status_code >= 500:
                    logger.exception(f"API connection error. url: {self.base_url}, Retry: {i}")
                    time.sleep(3)
                    i += 1
                    continue
                else:
                    break
            except json.decoder.JSONDecodeError:
                logger.exception(f"Failed to parse response from OpenAI API. url: {self.base_url}, Retry: {i}")
                time.sleep(3)
                i += 1
                continue
            except Exception as e:
                logger.exception(f"OpenAI API Unknown error. url: {self.base_url}")
                break
        
        return None
                
            


if __name__ == '__main__':
    from ve.common import config

    system_prompt = f"You are a Netflix subtitle translator. Please translate the following {'English'} sentence into {'Chinese'}. Do not provide any additional explanations, improvements, comments, notes or suggestions. Only provide the finally translation."
    user_prompt = "Well, here's an example from one of our smokers."

    api_key = config.get_config('gpt')['apiKey']
    model = config.get_config('gpt')['model']

    api = OpenAPI(model, api_key)
    print(api.completions(system_prompt, user_prompt))
