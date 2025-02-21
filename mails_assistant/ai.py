import threading
from abc import ABC

import openai

from mails_assistant import LLM_INSTRUCTIONS, OPENAI_API_KEY

class BaseLLM(ABC):
    pass


class OpenAILLM(BaseLLM):
    __instance = None
    __lock = threading.Lock()

    def __init__(self):
        if self.__initialized:
            return
        
        self.client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

        self.__initialized = True

    def __new__(cls, *args, **kwargs):
        with cls.__lock:
            if cls.__instance is None:
                cls.__instance = super().__new__(cls, *args, **kwargs)
                cls.__instance.__initialized = False
        return cls.__instance

    async def generate_response(self, content: str, *args, **kwargs) -> str:
        completion = await self.client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {
                    'role': 'system',
                    'content': LLM_INSTRUCTIONS,
                },
                {
                    'role': 'user',
                    'content': content, 
                },
            ],
            *args,
            **kwargs,
        )

        return completion.choices[0].message.content
