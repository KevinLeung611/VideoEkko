import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ve.gpt import deepseek_api
from ve.gpt import silicon_api
from ve.gpt import ollama_api
from ve.gpt import open_api


class GptFactory:

    def __init__(self, gpt_platform):
        self.gpt_platform = gpt_platform

    def generate_api(self, model, api_key):
        if self.gpt_platform == "silicon":
            return silicon_api.SiliconAPI(model, api_key)
        elif self.gpt_platform == "deepseek":
            return deepseek_api.DeepSeekAPI(model, api_key)
        elif self.gpt_platform == "ollama":
            return ollama_api.OllamaAPI(model)
        elif self.gpt_platform == 'openai':
            return open_api.OpenAPI(model, api_key)
        else:
            raise ValueError("Unknown GPT platform")
