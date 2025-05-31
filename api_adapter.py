from abc import ABC, abstractmethod
import aiohttp
import logging

logger = logging.getLogger(__name__)

class BaseAdapter(ABC):
    @abstractmethod
    async def chat_completion(self, messages: list, model: str) -> str:
        pass

class OllamaAdapter(BaseAdapter):
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url

    async def chat_completion(self, messages: list, model: str) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            try:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                ) as response:
                    result = await response.json()
                    return result['message']['content']
            except Exception as e:
                logger.error(f"Ollama请求失败: {str(e)}")
                raise

class OpenAIAdapter(BaseAdapter):
    def __init__(self, api_key: str, base_url="https://api.openai.com/v1"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def chat_completion(self, messages: list, model: str) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "messages": messages
            }
            try:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=self.headers
                ) as response:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
            except Exception as e:
                logger.error(f"OpenAI请求失败: {str(e)}")
                raise

class AnthropicAdapter(BaseAdapter):
    def __init__(self, api_key: str, base_url="https://api.anthropic.com"):
        self.base_url = base_url
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }

    async def chat_completion(self, messages: list, model: str) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": 1000
            }
            try:
                async with session.post(
                    f"{self.base_url}/v1/messages",
                    json=payload,
                    headers=self.headers
                ) as response:
                    result = await response.json()
                    return result['content'][0]['text']
            except Exception as e:
                logger.error(f"Anthropic请求失败: {str(e)}")
                raise

class MetaAdapter(BaseAdapter):
    def __init__(self, api_key: str, base_url="https://api.meta.ai"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def chat_completion(self, messages: list, model: str) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "messages": messages
            }
            try:
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=self.headers
                ) as response:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
            except Exception as e:
                logger.error(f"Meta请求失败: {str(e)}")
                raise

class GoogleAdapter(BaseAdapter):
    def __init__(self, api_key: str, base_url="https://generativelanguage.googleapis.com"):
        self.base_url = base_url
        self.api_key = api_key

    async def chat_completion(self, messages: list, model: str) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "messages": messages
            }
            try:
                async with session.post(
                    f"{self.base_url}/v1beta/models/{model}:generateMessage?key={self.api_key}",
                    json=payload
                ) as response:
                    result = await response.json()
                    return result['candidates'][0]['content']
            except Exception as e:
                logger.error(f"Google请求失败: {str(e)}")
                raise

class CohereAdapter(BaseAdapter):
    def __init__(self, api_key: str, base_url="https://api.cohere.ai"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def chat_completion(self, messages: list, model: str) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "message": messages[-1]['content'],
                "chat_history": messages[:-1]
            }
            try:
                async with session.post(
                    f"{self.base_url}/v1/chat",
                    json=payload,
                    headers=self.headers
                ) as response:
                    result = await response.json()
                    return result['text']
            except Exception as e:
                logger.error(f"Cohere请求失败: {str(e)}")
                raise

class ReplicateAdapter(BaseAdapter):
    def __init__(self, api_key: str, base_url="https://api.replicate.com"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json"
        }

    async def chat_completion(self, messages: list, model: str) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "input": {
                    "messages": messages,
                    "model": model
                }
            }
            try:
                async with session.post(
                    f"{self.base_url}/v1/predictions",
                    json=payload,
                    headers=self.headers
                ) as response:
                    result = await response.json()
                    return result['output'][0]
            except Exception as e:
                logger.error(f"Replicate请求失败: {str(e)}")
                raise

class AliyunAdapter(BaseAdapter):
    def __init__(self, api_key: str, base_url="https://dashscope.aliyuncs.com"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def chat_completion(self, messages: list, model: str) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "input": {
                    "messages": messages
                }
            }
            try:
                async with session.post(
                    f"{self.base_url}/api/v1/services/aigc/text-generation/generation",
                    json=payload,
                    headers=self.headers
                ) as response:
                    result = await response.json()
                    return result['output']['text']
            except Exception as e:
                logger.error(f"阿里云请求失败: {str(e)}")
                raise

class ZhipuAdapter(BaseAdapter):
    def __init__(self, api_key: str, base_url="https://open.bigmodel.cn"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def chat_completion(self, messages: list, model: str) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "messages": messages
            }
            try:
                async with session.post(
                    f"{self.base_url}/api/paas/v3/model-api/{model}/invoke",
                    json=payload,
                    headers=self.headers
                ) as response:
                    result = await response.json()
                    return result['data']['choices'][0]['message']['content']
            except Exception as e:
                logger.error(f"智谱请求失败: {str(e)}")
                raise

class MistralAdapter(BaseAdapter):
    def __init__(self, api_key: str, base_url="https://api.mistral.ai"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def chat_completion(self, messages: list, model: str) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "messages": messages
            }
            try:
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=self.headers
                ) as response:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
            except Exception as e:
                logger.error(f"Mistral请求失败: {str(e)}")
                raise

class DeepSeekAdapter(BaseAdapter):
    def __init__(self, api_key: str, base_url="https://api.deepseek.com"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def chat_completion(self, messages: list, model: str) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "messages": messages
            }
            try:
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=self.headers
                ) as response:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
            except Exception as e:
                logger.error(f"DeepSeek请求失败: {str(e)}")
                raise

class LambdaLabsAdapter(BaseAdapter):
    def __init__(self, api_key: str, base_url="https://cloud.lambdalabs.com"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def chat_completion(self, messages: list, model: str) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "messages": messages
            }
            try:
                async with session.post(
                    f"{self.base_url}/api/v1/chat/completions",
                    json=payload,
                    headers=self.headers
                ) as response:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
            except Exception as e:
                logger.error(f"Lambda Labs请求失败: {str(e)}")
                raise

class SiliconFlowAdapter(BaseAdapter):
    def __init__(self, api_key: str, base_url="https://api.siliconflow.cn"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def chat_completion(self, messages: list, model: str) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "messages": messages
            }
            try:
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=self.headers
                ) as response:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
            except Exception as e:
                logger.error(f"硅基流动请求失败: {str(e)}")
                raise

class OtherAdapter(BaseAdapter):
    def __init__(self, api_key: str, base_url: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def chat_completion(self, messages: list, model: str) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "messages": messages
            }
            try:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=self.headers
                ) as response:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
            except Exception as e:
                logger.error(f"自定义API请求失败: {str(e)}")
                raise