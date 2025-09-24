import os
from langchain_openai import ChatOpenAI
from typing import Optional
from pydantic import SecretStr, Field

class ChatOpenRouter(ChatOpenAI):
    def __init__(self, **kwargs):
        # Extrahiere base_url vor super().__init__
        base_url = kwargs.pop('base_url', "https://openrouter.ai/api/v1")
        
        super().__init__(
            base_url=base_url,
            **kwargs
        )

PROVIDERS = {
    "openrouter": ChatOpenRouter
}