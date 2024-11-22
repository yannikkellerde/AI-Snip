import os
import json
from typing import Optional, Type

from openai import AzureOpenAI, OpenAI
from openai._base_client import BaseClient
from openai.types.chat import ParsedChatCompletionMessage
from util import stream_wrapper
from model_wrapper import ModelWrapper

class OpenAIComplete(ModelWrapper):
    client: BaseClient
    def complete(self, messages: list[dict[str, str]], **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name, messages=messages, **kwargs
        )
        return response.choices[0].message.content
    
    def stream_complete(self, messages: list[dict[str, str]], **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name, messages=messages, stream=True, **kwargs
        )
        return stream_wrapper(response)
            
class OpenAIModelWrapper(OpenAIComplete):
    def __init__(
        self,
        model_name: str = "gpt-4o",
        log_file=None,
        api_key=os.environ.get("OPENAI_API_KEY"),
    ):
        self.client = OpenAI(
            api_key=api_key,
        )
        super().__init__(self.client, model_name)


class AzureModelWrapper(OpenAIComplete):
    def __init__(
        self,
        model_name: str = "gpt-4o",
        log_file=None,
        api_version="2024-08-01-preview",
    ):
        self.client = AzureOpenAI(
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version=api_version,
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        )
        super().__init__(self.client, model_name)
