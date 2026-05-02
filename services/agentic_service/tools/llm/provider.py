# from abc import ABC, abstractmethod
# import os
# import httpx
# from dotenv import load_dotenv

# load_dotenv()


# class LLMProvider(ABC):
#     @abstractmethod
#     async def generate(self, prompt: str) -> str:
#         pass


# class OllamaProvider(LLMProvider):
#     def __init__(self):
#         self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
#         self.model = os.getenv("OLLAMA_MODEL", "qwen3-coder")

#     async def generate(self, prompt: str) -> str:
#         async with httpx.AsyncClient(timeout=120) as client:
#             response = await client.post(
#                 f"{self.base_url}/api/generate",
#                 json={
#                     "model": self.model,
#                     "prompt": prompt,
#                     "stream": False
#                 }
#             )
#             response.raise_for_status()
#             return response.json()["response"]

##=======================================================Tharuk's edits start here=======================================================##

# import os
# from abc import ABC, abstractmethod

# import httpx
# from dotenv import load_dotenv

# load_dotenv()


# class LLMProvider(ABC):
#     """
#     Abstract LLM provider interface.

#     The Security Agent currently uses this synchronously from the CLI.
#     """

#     @abstractmethod
#     def generate(self, prompt: str) -> str:
#         pass


# class OllamaProvider(LLMProvider):
#     """
#     Synchronous Ollama HTTP provider.

#     Uses local Ollama endpoint:
#     http://localhost:11434/api/generate
#     """

#     def __init__(self):
#         self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
#         self.model = os.getenv("OLLAMA_MODEL", "llama3")

#     async def generate(self, prompt: str) -> str:
#         payload = {
#             "model": self.model,
#             "prompt": prompt,
#             "stream": False
#         }

#         async with httpx.AsyncClient(timeout=180) as client:
#             response = client.post(
#                 f"{self.base_url}/api/generate",
#                 json=payload
#             )
#             response.raise_for_status()
#             data = response.json()

#         return data.get("response", "")

#=======================================================Dulneth's edits end here=======================================================##
import os
from abc import ABC, abstractmethod

import httpx
from dotenv import load_dotenv

load_dotenv()


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str) -> str:
        pass


class OllamaProvider(LLMProvider):
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3")

    async def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.2
            }
        }

        async with httpx.AsyncClient(timeout=240) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )

        response.raise_for_status()
        data = response.json()

        return data.get("response", "")