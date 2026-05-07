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
import json
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
        self.model = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")  # ✅ updated default model

    async def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.1,       # ✅ lowered: more deterministic code output
                "num_ctx": 16384,         # ✅ increased: use qwen2.5-coder's large context window
                "num_predict": 6000,      # ✅ increased: prevents mid-file cutoff
                "top_p": 0.9,             # ✅ added: better token selection
                "top_k": 40,              # ✅ added: limits token candidates for quality
                "repeat_penalty": 1.1,    # ✅ added: prevents looping/repetitive output
                "num_keep": 24            # ✅ added: matches model's recommended num_keep
            }
        }

        timeout = httpx.Timeout(
            connect=30.0,
            read=900.0,    # ✅ increased: 15 min — CPU inference needs more time
            write=30.0,
            pool=30.0
        )

        chunks = []

        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if not line:
                        continue

                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue  # ✅ added: safely skip malformed lines

                    if "response" in data:
                        chunks.append(data["response"])

                    if data.get("done") is True:
                        break

        return "".join(chunks)


# ✅ added: FastAPI dependency injection helper
def get_llm_provider() -> LLMProvider:
    return OllamaProvider()