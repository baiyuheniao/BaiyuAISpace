# 从 abc 模块导入 ABC（抽象基类）和 abstractmethod（抽象方法）
from abc import ABC, abstractmethod
# 导入 aiohttp 库，用于异步 HTTP 请求
import aiohttp
# 导入 logging 库，用于日志记录
import logging

# 获取一个 logger 实例，用于记录日志
logger = logging.getLogger(__name__)

# 定义一个抽象基类 BaseAdapter，继承自 ABC
class BaseAdapter(ABC):
    # 定义一个抽象方法 chat_completion，所有继承此类的子类都必须实现此方法
    @abstractmethod
    async def chat_completion(self, messages: list, model: str) -> str:
        pass

# 定义 OllamaAdapter 类，继承自 BaseAdapter
class OllamaAdapter(BaseAdapter):
    # 构造函数，初始化 Ollama 服务的基准 URL
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url

    # 实现 chat_completion 抽象方法，用于与 Ollama 服务进行聊天补全
    async def chat_completion(self, messages: list, model: str) -> str:
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "model": model,  # 模型名称
                "messages": messages,  # 消息列表
                "stream": False  # 不使用流式传输
            }
            try:
                # 发送 POST 请求到 Ollama 的 /api/chat 接口
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload
                ) as response:
                    # 解析 JSON 响应
                    result = await response.json()
                    # 返回聊天补全结果
                    return result['message']['content']
            except Exception as e:
                # 捕获异常并记录错误日志
                logger.error(f"Ollama请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 OpenAIAdapter 类，继承自 BaseAdapter
class OpenAIAdapter(BaseAdapter):
    # 构造函数，初始化 OpenAI API 密钥和基准 URL
    def __init__(self, api_key: str, base_url="https://api.openai.com/v1"):
        self.base_url = base_url
        # 设置请求头，包含授权信息和内容类型
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    # 实现 chat_completion 抽象方法，用于与 OpenAI 服务进行聊天补全
    async def chat_completion(self, messages: list, model: str) -> str:
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "model": model,  # 模型名称
                "messages": messages  # 消息列表
            }
            try:
                # 发送 POST 请求到 OpenAI 的 /chat/completions 接口
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=self.headers
                ) as response:
                    # 解析 JSON 响应
                    result = await response.json()
                    # 返回聊天补全结果
                    return result['choices'][0]['message']['content']
            except Exception as e:
                # 捕获异常并记录错误日志
                logger.error(f"OpenAI请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 AnthropicAdapter 类，继承自 BaseAdapter
class AnthropicAdapter(BaseAdapter):
    # 构造函数，初始化 Anthropic API 密钥和基准 URL
    def __init__(self, api_key: str, base_url="https://api.anthropic.com"):
        self.base_url = base_url
        # 设置请求头，包含授权信息和内容类型
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }

    # 实现 chat_completion 抽象方法，用于与 Anthropic 服务进行聊天补全
    async def chat_completion(self, messages: list, model: str) -> str:
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "model": model,  # 模型名称
                "messages": messages,  # 消息列表
                "max_tokens": 1000  # 最大 token 数量
            }
            try:
                # 发送 POST 请求到 Anthropic 的 /v1/messages 接口
                async with session.post(
                    f"{self.base_url}/v1/messages",
                    json=payload,
                    headers=self.headers
                ) as response:
                    # 解析 JSON 响应
                    result = await response.json()
                    # 返回聊天补全结果
                    return result['content'][0]['text']
            except Exception as e:
                # 捕获异常并记录错误日志
                logger.error(f"Anthropic请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 MetaAdapter 类，继承自 BaseAdapter
class MetaAdapter(BaseAdapter):
    # 构造函数，初始化 Meta API 密钥和基准 URL
    def __init__(self, api_key: str, base_url="https://api.meta.ai"):
        self.base_url = base_url
        # 设置请求头，包含授权信息和内容类型
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    # 实现 chat_completion 抽象方法，用于与 Meta 服务进行聊天补全
    async def chat_completion(self, messages: list, model: str) -> str:
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "model": model,  # 模型名称
                "messages": messages  # 消息列表
            }
            try:
                # 发送 POST 请求到 Meta 的 /v1/chat/completions 接口
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=self.headers
                ) as response:
                    # 解析 JSON 响应
                    result = await response.json()
                    # 返回聊天补全结果
                    return result['choices'][0]['message']['content']
            except Exception as e:
                # 捕获异常并记录错误日志
                logger.error(f"Meta请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 GoogleAdapter 类，继承自 BaseAdapter
class GoogleAdapter(BaseAdapter):
    # 构造函数，初始化 Google API 密钥和基准 URL
    def __init__(self, api_key: str, base_url="https://generativelanguage.googleapis.com"):
        self.base_url = base_url
        self.api_key = api_key

    # 实现 chat_completion 抽象方法，用于与 Google 服务进行聊天补全
    async def chat_completion(self, messages: list, model: str) -> str:
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "model": model,  # 模型名称
                "messages": messages  # 消息列表
            }
            try:
                # 发送 POST 请求到 Google 的 /v1beta/models/{model}:generateMessage 接口
                async with session.post(
                    f"{self.base_url}/v1beta/models/{model}:generateMessage?key={self.api_key}",
                    json=payload
                ) as response:
                    # 解析 JSON 响应
                    result = await response.json()
                    # 返回聊天补全结果
                    return result['candidates'][0]['content']
            except Exception as e:
                # 捕获异常并记录错误日志
                logger.error(f"Google请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 CohereAdapter 类，继承自 BaseAdapter
class CohereAdapter(BaseAdapter):
    # 构造函数，初始化 Cohere API 密钥和基准 URL
    def __init__(self, api_key: str, base_url="https://api.cohere.ai"):
        self.base_url = base_url
        # 设置请求头，包含授权信息和内容类型
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    # 实现 chat_completion 抽象方法，用于与 Cohere 服务进行聊天补全
    async def chat_completion(self, messages: list, model: str) -> str:
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "model": model,  # 模型名称
                "message": messages[-1]['content'],  # 最新消息内容
                "chat_history": messages[:-1]  # 聊天历史
            }
            try:
                # 发送 POST 请求到 Cohere 的 /v1/chat 接口
                async with session.post(
                    f"{self.base_url}/v1/chat",
                    json=payload,
                    headers=self.headers
                ) as response:
                    # 解析 JSON 响应
                    result = await response.json()
                    # 返回聊天补全结果
                    return result['text']
            except Exception as e:
                # 捕获异常并记录错误日志
                logger.error(f"Cohere请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 ReplicateAdapter 类，继承自 BaseAdapter
class ReplicateAdapter(BaseAdapter):
    # 构造函数，初始化 Replicate API 密钥和基准 URL
    def __init__(self, api_key: str, base_url="https://api.replicate.com"):
        self.base_url = base_url
        # 设置请求头，包含授权信息和内容类型
        self.headers = {
            "Authorization": f"Token {api_key}",
            "Content-Type": "application/json"
        }

    # 实现 chat_completion 抽象方法，用于与 Replicate 服务进行聊天补全
    async def chat_completion(self, messages: list, model: str) -> str:
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "input": {
                    "messages": messages,  # 消息列表
                    "model": model  # 模型名称
                }
            }
            try:
                # 发送 POST 请求到 Replicate 的 /v1/predictions 接口
                async with session.post(
                    f"{self.base_url}/v1/predictions",
                    json=payload,
                    headers=self.headers
                ) as response:
                    # 解析 JSON 响应
                    result = await response.json()
                    # 返回聊天补全结果
                    return result['output'][0]
            except Exception as e:
                # 捕获异常并记录错误日志
                logger.error(f"Replicate请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 AliyunAdapter 类，继承自 BaseAdapter
class AliyunAdapter(BaseAdapter):
    # 构造函数，初始化阿里云 API 密钥和基准 URL
    def __init__(self, api_key: str, base_url="https://dashscope.aliyuncs.com"):
        self.base_url = base_url
        # 设置请求头，包含授权信息和内容类型
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    # 实现 chat_completion 抽象方法，用于与阿里云服务进行聊天补全
    async def chat_completion(self, messages: list, model: str) -> str:
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "model": model,  # 模型名称
                "input": {
                    "messages": messages  # 消息列表
                },
                "parameters": {
                    "result_format": "message"
                }
            }
            try:
                # 发送 POST 请求到阿里云的 /api/v1/services/aigc/chat/completion 接口
                async with session.post(
                    f"{self.base_url}/api/v1/services/aigc/chat/completion",
                    json=payload,
                    headers=self.headers
                ) as response:
                    # 解析 JSON 响应
                    result = await response.json()
                    # 返回聊天补全结果
                    return result['output']['choices'][0]['message']['content']
            except Exception as e:
                # 捕获异常并记录错误日志
                logger.error(f"Aliyun请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 BaiduAdapter 类，继承自 BaseAdapter
class BaiduAdapter(BaseAdapter):
    # 构造函数，初始化百度 API 密钥和基准 URL
    def __init__(self, api_key: str, secret_key: str, base_url="https://aip.baidubce.com"):
        self.base_url = base_url
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None

    # 异步方法，用于获取百度访问令牌
    async def _get_access_token(self):
        # 如果访问令牌已存在，则直接返回
        if self.access_token:
            return self.access_token

        # 构建请求 URL
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}"
        async with aiohttp.ClientSession() as session:
            async with session.post(url) as response:
                result = await response.json()
                self.access_token = result.get("access_token")
                return self.access_token

    # 实现 chat_completion 抽象方法，用于与百度服务进行聊天补全
    async def chat_completion(self, messages: list, model: str) -> str:
        # 获取访问令牌
        access_token = await self._get_access_token()
        if not access_token:
            raise Exception("无法获取百度访问令牌")

        # 构建请求 URL
        url = f"{self.base_url}/rpc/2.0/ai_nlp/v1/chat/completions_pro?access_token={access_token}"
        # 构建请求体 payload
        payload = {
            "messages": messages  # 消息列表
        }
        async with aiohttp.ClientSession() as session:
            try:
                # 发送 POST 请求到百度聊天补全接口
                async with session.post(
                    url,
                    json=payload
                ) as response:
                    # 解析 JSON 响应
                    result = await response.json()
                    # 返回聊天补全结果
                    return result['result']['content']
            except Exception as e:
                # 捕获异常并记录错误日志
                logger.error(f"Baidu请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 DeepSeekAdapter 类，继承自 BaseAdapter
class DeepSeekAdapter(BaseAdapter):
    # 构造函数，初始化 DeepSeek API 密钥和基准 URL
    def __init__(self, api_key: str, base_url="https://api.deepseek.com"):
        self.base_url = base_url
        # 设置请求头，包含授权信息和内容类型
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    # 实现 chat_completion 抽象方法，用于与 DeepSeek 服务进行聊天补全
    async def chat_completion(self, messages: list, model: str) -> str:
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "model": model,  # 模型名称
                "messages": messages,  # 消息列表
                "stream": False  # 不使用流式传输
            }
            try:
                # 发送 POST 请求到 DeepSeek 的 /chat/completions 接口
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=self.headers
                ) as response:
                    # 解析 JSON 响应
                    result = await response.json()
                    # 返回聊天补全结果
                    return result['choices'][0]['message']['content']
            except Exception as e:
                # 捕获异常并记录错误日志
                logger.error(f"DeepSeek请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 MoonshotAdapter 类，继承自 BaseAdapter
class MoonshotAdapter(BaseAdapter):
    # 构造函数，初始化 Moonshot API 密钥和基准 URL
    def __init__(self, api_key: str, base_url="https://api.moonshot.cn"):
        self.base_url = base_url
        # 设置请求头，包含授权信息和内容类型
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    # 实现 chat_completion 抽象方法，用于与 Moonshot 服务进行聊天补全
    async def chat_completion(self, messages: list, model: str) -> str:
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "model": model,  # 模型名称
                "messages": messages,  # 消息列表
                "stream": False  # 不使用流式传输
            }
            try:
                # 发送 POST 请求到 Moonshot 的 /v1/chat/completions 接口
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=self.headers
                ) as response:
                    # 解析 JSON 响应
                    result = await response.json()
                    # 返回聊天补全结果
                    return result['choices'][0]['message']['content']
            except Exception as e:
                # 捕获异常并记录错误日志
                logger.error(f"Moonshot请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 ZhipuAdapter 类，继承自 BaseAdapter
class ZhipuAdapter(BaseAdapter):
    # 构造函数，初始化智谱 API 密钥和基准 URL
    def __init__(self, api_key: str, base_url="https://open.bigmodel.cn"):
        self.base_url = base_url
        # 设置请求头，包含授权信息和内容类型
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    # 实现 chat_completion 抽象方法，用于与智谱服务进行聊天补全
    async def chat_completion(self, messages: list, model: str) -> str:
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "model": model,  # 模型名称
                "messages": messages,  # 消息列表
                "stream": False  # 不使用流式传输
            }
            try:
                # 发送 POST 请求到智谱的 /api/paas/v3/model-api/{model}/sse-invoke 接口
                async with session.post(
                    f"{self.base_url}/api/paas/v3/model-api/{model}/sse-invoke",
                    json=payload,
                    headers=self.headers
                ) as response:
                    # 解析 JSON 响应
                    result = await response.json()
                    # 返回聊天补全结果
                    return result['choices'][0]['message']['content']
            except Exception as e:
                # 捕获异常并记录错误日志
                logger.error(f"Zhipu请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 SparkAdapter 类，继承自 BaseAdapter
class SparkAdapter(BaseAdapter):
    # 构造函数，初始化 Spark API 密钥和基准 URL
    def __init__(self, api_key: str, base_url="https://spark-api.xf-yun.com"):
        self.base_url = base_url
        # 设置请求头，包含授权信息和内容类型
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    # 实现 chat_completion 抽象方法，用于与 Spark 服务进行聊天补全
    async def chat_completion(self, messages: list, model: str) -> str:
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "model": model,  # 模型名称
                "messages": messages,  # 消息列表
                "stream": False  # 不使用流式传输
            }
            try:
                # 发送 POST 请求到 Spark 的 /v3.5/chat 接口
                async with session.post(
                    f"{self.base_url}/v3.5/chat",
                    json=payload,
                    headers=self.headers
                ) as response:
                    # 解析 JSON 响应
                    result = await response.json()
                    # 返回聊天补全结果
                    return result['choices'][0]['message']['content']
            except Exception as e:
                # 捕获异常并记录错误日志
                logger.error(f"Spark请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 MinimaxAdapter 类，继承自 BaseAdapter
class MinimaxAdapter(BaseAdapter):
    # 构造函数，初始化 Minimax API 密钥和基准 URL
    def __init__(self, api_key: str, base_url="https://api.minimax.chat"):
        self.base_url = base_url
        # 设置请求头，包含授权信息和内容类型
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    # 实现 chat_completion 抽象方法，用于与 Minimax 服务进行聊天补全
    async def chat_completion(self, messages: list, model: str) -> str:
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "model": model,  # 模型名称
                "messages": messages,  # 消息列表
                "stream": False  # 不使用流式传输
            }
            try:
                # 发送 POST 请求到 Minimax 的 /v1/chat/completions 接口
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=self.headers
                ) as response:
                    # 解析 JSON 响应
                    result = await response.json()
                    # 返回聊天补全结果
                    return result['choices'][0]['message']['content']
            except Exception as e:
                # 捕获异常并记录错误日志
                logger.error(f"Minimax请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 SenseChatAdapter 类，继承自 BaseAdapter
class SenseChatAdapter(BaseAdapter):
    # 构造函数，初始化 SenseChat API 密钥和基准 URL
    def __init__(self, api_key: str, base_url="https://api.sensetime.com"):
        self.base_url = base_url
        # 设置请求头，包含授权信息和内容类型
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    # 实现 chat_completion 抽象方法，用于与 SenseChat 服务进行聊天补全
    async def chat_completion(self, messages: list, model: str) -> str:
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "model": model,  # 模型名称
                "messages": messages,  # 消息列表
                "stream": False  # 不使用流式传输
            }
            try:
                # 发送 POST 请求到 SenseChat 的 /v1/chat/completions 接口
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=self.headers
                ) as response:
                    # 解析 JSON 响应
                    result = await response.json()
                    # 返回聊天补全结果
                    return result['choices'][0]['message']['content']
            except Exception as e:
                # 捕获异常并记录错误日志
                logger.error(f"SenseChat请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 XunfeiAdapter 类，继承自 BaseAdapter
class XunfeiAdapter(BaseAdapter):
    # 构造函数，初始化讯飞 API 密钥和基准 URL
    def __init__(self, api_key: str, base_url="https://api.xf-yun.com"):
        self.base_url = base_url
        # 设置请求头，包含授权信息和内容类型
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    # 实现 chat_completion 抽象方法，用于与讯飞服务进行聊天补全
    async def chat_completion(self, messages: list, model: str) -> str:
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "model": model,  # 模型名称
                "messages": messages,  # 消息列表
                "stream": False  # 不使用流式传输
            }
            try:
                # 发送 POST 请求到讯飞的 /v1/chat/completions 接口
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=self.headers
                ) as response:
                    # 解析 JSON 响应
                    result = await response.json()
                    # 返回聊天补全结果
                    return result['choices'][0]['message']['content']
            except Exception as e:
                # 捕获异常并记录错误日志
                logger.error(f"Xunfei请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 CustomAdapter 类，继承自 BaseAdapter
class CustomAdapter(BaseAdapter):
    # 构造函数，初始化自定义 API 密钥和基准 URL
    def __init__(self, api_key: str, base_url: str):
        self.base_url = base_url
        # 设置请求头，包含授权信息和内容类型
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    # 实现 chat_completion 抽象方法，用于与自定义服务进行聊天补全
    async def chat_completion(self, messages: list, model: str) -> str:
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "model": model,  # 模型名称
                "messages": messages,  # 消息列表
                "stream": False  # 不使用流式传输
            }
            try:
                # 发送 POST 请求到自定义服务的 /v1/chat/completions 接口
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=self.headers
                ) as response:
                    # 解析 JSON 响应
                    result = await response.json()
                    # 返回聊天补全结果
                    return result['choices'][0]['message']['content']
            except Exception as e:
                # 捕获异常并记录错误日志
                logger.error(f"Custom请求失败: {str(e)}")
                # 重新抛出异常
                raise