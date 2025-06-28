# 从 abc 模块导入 ABC（抽象基类）和 abstractmethod（抽象方法）
from abc import ABC, abstractmethod
# 导入 aiohttp 库，用于异步 HTTP 请求
import aiohttp
# 导入 logging 库，用于日志记录
import logging
# 导入 time 库，用于时间戳和过期检查
import time
# 导入 json 库，用于解析响应
import json
# 导入 typing 库，用于类型注解
from typing import Optional, List, Union

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
    def __init__(self, api_key: str, base_url="https://api.openai.com/v1", organization_id=None):
        if not api_key or not isinstance(api_key, str):
            raise ValueError("OpenAI API密钥不能为空且必须是字符串")
        
        self.base_url = base_url
        # 设置请求头，包含授权信息和内容类型
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # 如果提供了组织ID，添加到请求头中
        if organization_id:
            self.headers["OpenAI-Organization"] = organization_id
            
        logger.debug(f"已初始化OpenAI适配器，API基础URL: {base_url}")

    # 实现 chat_completion 抽象方法，用于与 OpenAI 服务进行聊天补全
    async def chat_completion(self, messages: list, model: str, temperature=0.7, max_tokens=None, 
                             top_p=1.0, frequency_penalty=0, presence_penalty=0, stop=None) -> str:
        # 验证消息列表
        if not messages or not isinstance(messages, list):
            logger.error("OpenAI请求错误: 消息列表为空或格式不正确")
            raise ValueError("消息列表为空或格式不正确")
            
        # 验证模型名称
        if not model or not isinstance(model, str):
            logger.error("OpenAI请求错误: 模型名称无效")
            raise ValueError("模型名称无效")
            
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "model": model,        # 模型名称
                "messages": messages,  # 消息列表
                "temperature": temperature,  # 控制随机性
                "top_p": top_p,        # 核采样
                "frequency_penalty": frequency_penalty,  # 频率惩罚
                "presence_penalty": presence_penalty     # 存在惩罚
            }
            
            # 只有在提供了有效值时才添加这些参数
            if max_tokens is not None and max_tokens > 0:
                payload["max_tokens"] = max_tokens
                
            if stop and (isinstance(stop, str) or isinstance(stop, list)):
                payload["stop"] = stop
                
            try:
                logger.debug(f"向OpenAI发送请求: {model}, 消息数: {len(messages)}")
                
                # 发送 POST 请求到 OpenAI 的 /chat/completions 接口
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(60)  # 添加超时设置
                ) as response:
                    response_text = await response.text()
                    
                    # 检查响应状态码
                    if response.status != 200:
                        logger.error(f"OpenAI请求失败，状态码: {response.status}, 详情: {response_text}")
                        raise Exception(f"OpenAI API请求失败: {response.status} - {response_text}")
                    
                    # 解析 JSON 响应
                    try:
                        result = await response.json()
                    except Exception as e:
                        logger.error(f"OpenAI响应JSON解析失败: {str(e)}, 原始响应: {response_text}")
                        raise ValueError(f"无法解析OpenAI API响应: {str(e)}")
                    
                    # 检查结果格式
                    if not result or 'choices' not in result or not result['choices']:
                        logger.error(f"OpenAI响应缺少choices字段: {result}")
                        raise ValueError("OpenAI响应格式无效，缺少choices")
                    
                    # 返回聊天补全结果
                    choice = result['choices'][0]
                    if 'message' not in choice or 'content' not in choice['message']:
                        logger.error(f"OpenAI响应格式异常: {choice}")
                        raise ValueError("OpenAI响应格式无效，缺少message.content")
                        
                    # 添加使用量日志记录（如果存在）
                    if 'usage' in result:
                        logger.debug(f"OpenAI API使用情况: 输入tokens: {result['usage'].get('prompt_tokens', '未知')}, "
                                   f"输出tokens: {result['usage'].get('completion_tokens', '未知')}")
                        
                    return choice['message']['content']
                    
            except aiohttp.ClientError as e:
                logger.error(f"OpenAI请求客户端错误: {str(e)}")
                raise
            except Exception as e:
                # 捕获异常并记录错误日志
                logger.error(f"OpenAI请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 AnthropicAdapter 类，继承自 BaseAdapter
class AnthropicAdapter(BaseAdapter):
    # 构造函数，初始化 Anthropic API 密钥和基准 URL
    def __init__(self, api_key: str, base_url="https://api.anthropic.com", api_version="2023-06-01"):
        if not api_key or not isinstance(api_key, str):
            raise ValueError("Anthropic API密钥不能为空且必须是字符串")
            
        self.base_url = base_url
        self.api_version = api_version
        
        # 设置请求头，包含授权信息和内容类型（符合最新的Anthropic API规范）
        self.headers = {
            "x-api-key": api_key,
            "anthropic-version": api_version,  # 添加API版本头
            "Content-Type": "application/json"
        }
        
        logger.debug(f"已初始化Anthropic适配器，API基础URL: {base_url}, API版本: {api_version}")

    # 将OpenAI格式的消息转换为Anthropic格式
    def _convert_messages(self, messages):
        if not messages:
            return []
            
        # 提取系统消息（如果存在）
        system_content = None
        chat_messages = []
        
        for msg in messages:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                logger.warning(f"跳过无效消息格式: {msg}")
                continue
                
            role = msg['role']
            content = msg['content']
            
            if role == 'system':
                system_content = content
            else:
                # 将OpenAI角色映射到Anthropic角色
                anthropic_role = 'assistant' if role == 'assistant' else 'user'
                chat_messages.append({"role": anthropic_role, "content": content})
        
        return chat_messages, system_content

    # 实现 chat_completion 抽象方法，用于与 Anthropic 服务进行聊天补全
    async def chat_completion(self, messages: list, model: str, **kwargs) -> str:
        # 验证输入
        if not messages or not isinstance(messages, list):
            logger.error("Anthropic请求错误: 消息列表为空或格式不正确")
            raise ValueError("消息列表为空或格式不正确")
            
        if not model or not isinstance(model, str):
            logger.error("Anthropic请求错误: 模型名称无效")
            raise ValueError("模型名称无效")
        
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 转换消息格式
            chat_messages, system_content = self._convert_messages(messages)
            
            if not chat_messages:
                logger.error("Anthropic请求错误: 转换后的消息列表为空")
                raise ValueError("转换后的消息列表为空")
                
            # 构建请求体 payload
            payload = {
                "model": model,         # 模型名称
                "messages": chat_messages,  # 消息列表
                "max_tokens": kwargs.get("max_tokens", 1000),  # 最大 token 数量
                "temperature": kwargs.get("temperature", 0.7), # 温度参数
                "top_p": kwargs.get("top_p", 1.0),            # top_p 参数
                "top_k": kwargs.get("top_k", -1)              # top_k 参数
            }
            
            # 如果存在系统消息，添加到payload
            if system_content:
                payload["system"] = system_content
                
            # 添加可选参数
            if "stop_sequences" in kwargs and kwargs["stop_sequences"]:
                payload["stop_sequences"] = kwargs["stop_sequences"]
                
            try:
                logger.debug(f"向Anthropic发送请求: {model}, 消息数: {len(chat_messages)}")
                
                # 发送 POST 请求到 Anthropic 的 /v1/messages 接口
                async with session.post(
                    f"{self.base_url}/v1/messages",
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(60)  # 添加超时设置
                ) as response:
                    response_text = await response.text()
                    
                    # 检查响应状态码
                    if response.status not in (200, 201):
                        logger.error(f"Anthropic请求失败，状态码: {response.status}，详情: {response_text}")
                        raise Exception(f"Anthropic API请求失败: {response.status} - {response_text}")
                    
                    # 解析 JSON 响应
                    try:
                        result = await response.json()
                    except Exception as e:
                        logger.error(f"Anthropic响应JSON解析失败: {str(e)}, 原始响应: {response_text}")
                        raise ValueError(f"无法解析Anthropic API响应: {str(e)}")
                    
                    # 验证响应格式
                    if 'content' not in result or not result['content'] or not isinstance(result['content'], list):
                        logger.error(f"Anthropic响应格式无效: {result}")
                        raise ValueError("Anthropic响应格式无效，缺少content字段或格式不正确")
                    
                    # 提取文本内容
                    for content_item in result['content']:
                        if content_item.get('type') == 'text':
                            return content_item.get('text', '')
                    
                    # 如果没有找到文本内容，使用旧版格式尝试
                    if result['content'][0].get('text'):
                        return result['content'][0]['text']
                        
                    logger.warning(f"无法从Anthropic响应中提取文本内容: {result}")
                    return ""
                    
            except aiohttp.ClientError as e:
                # 捕获 aiohttp 客户端错误
                logger.error(f"Anthropic请求客户端错误: {str(e)}")
                raise
            except Exception as e:
                # 捕获其他未知异常并记录错误日志
                logger.error(f"Anthropic请求发生未知错误: {str(e)}")
                raise

# 定义 MetaAdapter 类，继承自 BaseAdapter
class MetaAdapter(BaseAdapter):
    # 构造函数，初始化 Meta API 密钥和基准 URL
    def __init__(self, api_key: str, base_url="https://llama.meta.ai/v1"):
        if not api_key or not isinstance(api_key, str):
            raise ValueError("Meta API密钥不能为空且必须是字符串")
            
        self.base_url = base_url
        # 设置请求头，包含授权信息和内容类型
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        logger.debug(f"已初始化Meta适配器，API基础URL: {base_url}")

    # 实现 chat_completion 抽象方法，用于与 Meta 服务进行聊天补全
    async def chat_completion(self, messages: list, model: str, **kwargs) -> str:
        # 验证输入
        if not messages or not isinstance(messages, list):
            logger.error("Meta请求错误: 消息列表为空或格式不正确")
            raise ValueError("消息列表为空或格式不正确")
            
        if not model or not isinstance(model, str):
            logger.error("Meta请求错误: 模型名称无效")
            raise ValueError("模型名称无效")
        
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 验证消息格式
            valid_messages = []
            for msg in messages:
                if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                    logger.warning(f"跳过无效消息格式: {msg}")
                    continue
                    
                # Meta LLama API支持的角色: user, assistant, system
                if msg['role'] not in ['user', 'assistant', 'system']:
                    logger.warning(f"将未知角色 '{msg['role']}' 转换为 'user'")
                    msg = msg.copy()  # 创建副本以避免修改原始消息
                    msg['role'] = 'user'
                    
                valid_messages.append(msg)
                
            if not valid_messages:
                logger.error("Meta请求错误: 转换后的消息列表为空")
                raise ValueError("转换后的消息列表为空")
            
            # 构建请求体 payload
            payload = {
                "model": model,  # 模型名称
                "messages": valid_messages,  # 消息列表
                "temperature": kwargs.get("temperature", 0.7), # 温度参数
                "max_tokens": kwargs.get("max_tokens", 1000), # 最大 token 数量
                "top_p": kwargs.get("top_p", 1.0) # top_p 参数
            }
            
            # 添加可选参数
            if "stream" in kwargs:
                payload["stream"] = kwargs["stream"]
                
            if "stop" in kwargs and kwargs["stop"]:
                payload["stop"] = kwargs["stop"]
                
            try:
                logger.debug(f"向Meta发送请求: {model}, 消息数: {len(valid_messages)}")
                
                # 发送 POST 请求到 Meta 的 /chat/completions 接口
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(60)  # 添加超时设置
                ) as response:
                    response_text = await response.text()
                    
                    # 检查响应状态码
                    if response.status != 200:
                        logger.error(f"Meta请求失败，状态码: {response.status}，详情: {response_text}")
                        raise Exception(f"Meta API请求失败: {response.status} - {response_text}")
                    
                    # 解析 JSON 响应
                    try:
                        result = await response.json()
                    except Exception as e:
                        logger.error(f"Meta响应JSON解析失败: {str(e)}, 原始响应: {response_text}")
                        raise ValueError(f"无法解析Meta API响应: {str(e)}")
                    
                    # 验证响应格式
                    if not result or 'choices' not in result or not result['choices']:
                        logger.error(f"Meta响应格式无效: {result}")
                        raise ValueError("Meta响应格式无效，缺少choices字段")
                    
                    # 返回聊天补全结果
                    choice = result['choices'][0]
                    if 'message' not in choice or 'content' not in choice['message']:
                        logger.error(f"Meta响应格式异常: {choice}")
                        raise ValueError("Meta响应格式无效，缺少message.content")
                        
                    # 记录使用信息（如果存在）
                    if 'usage' in result:
                        logger.debug(f"Meta API使用情况: 输入tokens: {result['usage'].get('prompt_tokens', '未知')}, "
                                   f"输出tokens: {result['usage'].get('completion_tokens', '未知')}")
                    
                    return choice['message']['content']
                    
            except aiohttp.ClientError as e:
                # 捕获 aiohttp 客户端错误
                logger.error(f"Meta请求客户端错误: {str(e)}")
                raise
            except Exception as e:
                # 捕获其他未知异常并记录错误日志
                logger.error(f"Meta请求发生未知错误: {str(e)}")
                raise

# 定义 GoogleAdapter 类，继承自 BaseAdapter
class GoogleAdapter(BaseAdapter):
    # 构造函数，初始化 Google API 密钥和基准 URL
    def __init__(self, api_key: str, base_url="https://generativelanguage.googleapis.com"):
        self.base_url = base_url
        self.api_key = api_key
        # 角色映射字典，将OpenAI角色映射到Gemini角色
        self.role_mapping = {
            "user": "user",
            "assistant": "model",
            "system": "user"  # Gemini API没有专门的system角色，通常作为user消息处理
        }

    # 实现 chat_completion 抽象方法，用于与 Google 服务进行聊天补全
    async def chat_completion(self, messages: list, model: str, temperature: float = 0.7, top_p: float = 1.0, top_k: int = 0, max_output_tokens: int = 1024, stop_sequences: Optional[List[str]] = None) -> str:
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 验证消息列表非空
            if not messages or not isinstance(messages, list):
                logger.error("Google请求错误: 消息列表为空或格式不正确")
                raise ValueError("消息列表为空或格式不正确")

            # 将messages转换为Google Gemini API所需的contents格式
            contents = []
            for msg in messages:
                # 检查消息格式是否正确
                if not isinstance(msg, dict) or 'role' not in msg:
                    logger.warning(f"跳过无效消息格式: {msg}")
                    continue
                
                # 映射角色
                role = self.role_mapping.get(msg.get('role', ''), "user")
                
                # 确保content存在且非空
                if 'content' not in msg or not msg['content']:
                    logger.warning(f"跳过空内容消息: {msg}")
                    continue
                
                # 创建parts
                parts = [{"text": msg['content']}]
                contents.append({"role": role, "parts": parts})
            
            # 确保转换后的内容非空
            if not contents:
                logger.error("Google请求错误: 转换后的消息内容为空")
                raise ValueError("转换后的消息内容为空")

            # 构建请求体 payload
            payload = {
                "contents": contents,  # 消息列表
                "generationConfig": {
                    "temperature": temperature,
                    "topP": top_p,
                    "topK": top_k,
                    "maxOutputTokens": max_output_tokens,
                }
            }
            if stop_sequences and isinstance(stop_sequences, list):
                payload["generationConfig"]["stopSequences"] = stop_sequences

            try:
                # 使用v1版本API端点代替v1beta
                api_url = f"{self.base_url}/v1/models/{model}:generateContent?key={self.api_key}"
                logger.debug(f"向Google API发送请求: {api_url}")
                
                # 发送 POST 请求到 Google 的 /v1/models/{model}:generateContent 接口
                async with session.post(
                    api_url,
                    json=payload
                ) as response:
                    response_text = await response.text()
                    
                    if response.status != 200:
                        logger.error(f"Google请求失败，状态码: {response.status}, 详情: {response_text}")
                        raise Exception(f"Google API请求失败: {response.status} - {response_text}")

                    # 解析 JSON 响应
                    try:
                        result = await response.json()
                    except Exception as e:
                        logger.error(f"Google响应JSON解析失败: {str(e)}, 原始响应: {response_text}")
                        raise ValueError(f"无法解析Google API响应: {str(e)}")
                    
                    # 按照Gemini API的标准响应格式解析结果
                    if 'candidates' in result and result['candidates']:
                        candidate = result['candidates'][0]
                        
                        # 标准Gemini响应路径: candidates[0].content.parts[0].text
                        if 'content' in candidate and 'parts' in candidate['content']:
                            parts = candidate['content']['parts']
                            if parts and 'text' in parts[0]:
                                return parts[0]['text']
                        
                        # 备用路径检查
                        elif 'content' in candidate:
                            content = candidate['content']
                            if isinstance(content, str):
                                return content
                        
                        # 旧版API兼容性检查
                        elif 'parts' in candidate and candidate['parts']:
                            # 处理parts数组，提取文本内容
                            text_content = "".join([part['text'] for part in candidate['parts'] if 'text' in part])
                            if text_content:
                                return text_content
                    
                    # 检查是否存在finishReason为SAFETY
                    if 'candidates' in result and result['candidates'] and 'finishReason' in result['candidates'][0]:
                        finish_reason = result['candidates'][0]['finishReason']
                        if finish_reason == "SAFETY":
                            logger.warning("Google API由于安全原因拒绝生成响应")
                            return "很抱歉，我无法回答这个问题。"
                    
                    logger.warning(f"无法从Google API响应提取文本内容: {result}")
                    return "无法获取有效响应"
                    
            except aiohttp.ClientError as e:
                logger.error(f"Google请求客户端错误: {str(e)}")
                raise
            except Exception as e:
                # 捕获其他未知异常并记录错误日志
                logger.error(f"Google请求发生未知错误: {str(e)}")
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
        if not api_key or not isinstance(api_key, str):
            raise ValueError("百度 API Key不能为空且必须是字符串")
            
        if not secret_key or not isinstance(secret_key, str):
            raise ValueError("百度 Secret Key不能为空且必须是字符串")
            
        self.base_url = base_url
        self.api_key = api_key
        self.secret_key = secret_key
        self.access_token = None  # 访问令牌，初始为 None
        self.token_expires_at = 0  # 令牌过期时间戳
        
        logger.debug(f"已初始化百度文心适配器，API基础URL: {base_url}")

    # 异步方法，用于获取百度访问令牌，带有过期检查
    async def _get_access_token(self):
        # 如果访问令牌已存在且未过期，则直接返回
        current_time = int(time.time())
        if self.access_token and current_time < self.token_expires_at - 60:  # 预留60秒的缓冲时间
            return self.access_token

        # 构建请求 URL
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.api_key}&client_secret={self.secret_key}"
        
        async with aiohttp.ClientSession() as session:
            try:
                # 发送 POST 请求获取访问令牌
                async with session.post(url) as response:
                    if response.status != 200:
                        error_detail = await response.text()
                        logger.error(f"百度访问令牌获取失败，状态码: {response.status}，详情: {error_detail}")
                        raise Exception(f"百度访问令牌获取失败: {response.status} - {error_detail}")
                        
                    result = await response.json()
                    
                    if "access_token" not in result:
                        logger.error(f"百度访问令牌获取失败，返回数据格式异常: {result}")
                        raise ValueError("百度访问令牌获取失败，返回数据格式异常")
                    
                    # 设置访问令牌和过期时间
                    self.access_token = result["access_token"]
                    # 令牌有效期通常为30天，将其转换为时间戳
                    expires_in = result.get("expires_in", 2592000)  # 默认30天
                    self.token_expires_at = current_time + expires_in
                    
                    logger.debug(f"已获取新的百度访问令牌，有效期至: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.token_expires_at))}")
                    
                    return self.access_token
                    
            except Exception as e:
                logger.error(f"获取百度访问令牌时发生错误: {str(e)}")
                raise

    # 实现 chat_completion 抽象方法，用于与百度服务进行聊天补全
    async def chat_completion(self, messages: list, model: str, temperature=0.7, top_p=0.8, penalty_score=1.0) -> str:
        # 验证输入
        if not messages or not isinstance(messages, list):
            logger.error("百度请求错误: 消息列表为空或格式不正确")
            raise ValueError("消息列表为空或格式不正确")
            
        if not model or not isinstance(model, str):
            logger.error("百度请求错误: 模型名称无效")
            raise ValueError("模型名称无效")
        
        # 获取访问令牌
        try:
            access_token = await self._get_access_token()
            if not access_token:
                raise Exception("无法获取百度访问令牌")
        except Exception as e:
            logger.error(f"获取百度访问令牌失败: {str(e)}")
            raise

        # 验证消息格式
        valid_messages = []
        for msg in messages:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                logger.warning(f"跳过无效消息格式: {msg}")
                continue
            
            # 角色映射（百度文心使用的角色是user/assistant）
            role = msg['role']
            if role not in ['user', 'assistant']:
                if role == 'system':
                    # 将system消息作为user消息处理，但增加特殊标记
                    role = 'user'
                    logger.warning("百度文心API不直接支持system角色，已转换为user角色")
                else:
                    logger.warning(f"将未知角色 '{role}' 转换为 'user'")
                    role = 'user'
            
            valid_messages.append({
                "role": role,
                "content": msg['content']
            })
        
        if not valid_messages:
            logger.error("百度请求错误: 转换后的消息列表为空")
            raise ValueError("转换后的消息列表为空")
        
        # 构建请求体 payload
        payload: dict = {
            "messages": valid_messages  # 消息列表
        }
        
        # 添加可选参数
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if penalty_score is not None:
            payload["penalty_score"] = penalty_score
            
        # 构建适当的API URL，根据模型名称选择正确的端点
        if 'ernie-bot' in model or 'ERNIE-Bot' in model:
            api_url = f"{self.base_url}/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{model}?access_token={access_token}"
        else:
            # 默认使用通用的chat completions接口
            api_url = f"{self.base_url}/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/{model}?access_token={access_token}"
            
        logger.debug(f"向百度文心发送请求: {model}, 消息数: {len(valid_messages)}")
        
        async with aiohttp.ClientSession() as session:
            try:
                # 发送 POST 请求到百度聊天补全接口
                async with session.post(
                    api_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(60)  # 添加超时设置
                ) as response:
                    response_text = await response.text()
                    
                    # 检查响应状态码
                    if response.status != 200:
                        logger.error(f"百度请求失败，状态码: {response.status}，详情: {response_text}")
                        
                        # 如果是token失效错误，尝试刷新token并重试
                        try:
                            result_json = json.loads(response_text)
                            error_code = result_json.get('error_code', 0)
                            if error_code in [110, 111]:  # token过期或无效
                                logger.warning("百度访问令牌已过期，尝试刷新...")
                                self.access_token = None  # 重置token
                                return await self.chat_completion(messages, model, temperature, top_p, penalty_score)
                        except:
                            pass  # 如果无法解析为JSON，继续抛出原始错误
                            
                        raise Exception(f"百度API请求失败: {response.status} - {response_text}")
                    
                    # 解析 JSON 响应
                    try:
                        result = await response.json()
                    except Exception as e:
                        logger.error(f"百度响应JSON解析失败: {str(e)}, 原始响应: {response_text}")
                        raise ValueError(f"无法解析百度API响应: {str(e)}")
                    
                    # 检查错误信息
                    if 'error_code' in result and result['error_code'] != 0:
                        error_msg = result.get('error_msg', '未知错误')
                        logger.error(f"百度API返回错误: {result['error_code']} - {error_msg}")
                        raise Exception(f"百度API返回错误: {result['error_code']} - {error_msg}")
                    
                    # 不同的API版本可能有不同的响应格式
                    if 'result' in result:
                        # 基本响应格式
                        if isinstance(result['result'], str):
                            return result['result']
                        # 包含content字段的格式
                        elif isinstance(result['result'], dict) and 'content' in result['result']:
                            return result['result']['content']
                    
                    # 记录使用信息（如果存在）
                    if 'usage' in result:
                        logger.debug(f"百度API使用情况: 输入tokens: {result['usage'].get('prompt_tokens', '未知')}, "
                                   f"输出tokens: {result['usage'].get('completion_tokens', '未知')}")
                        
                    logger.error(f"无法从百度响应中提取文本内容: {result}")
                    return ""
                    
            except aiohttp.ClientError as e:
                # 捕获 aiohttp 客户端错误
                logger.error(f"百度请求客户端错误: {str(e)}")
                raise
            except Exception as e:
                # 捕获其他未知异常并记录错误日志
                logger.error(f"百度请求失败: {str(e)}")
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
        if not api_key or not isinstance(api_key, str):
            raise ValueError("Moonshot API密钥不能为空且必须是字符串")
            
        self.base_url = base_url
        self.api_key = api_key
        
        # 设置请求头，包含授权信息和内容类型
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        logger.debug(f"已初始化Moonshot适配器，API基础URL: {base_url}")

    # 实现 chat_completion 抽象方法，用于与 Moonshot 服务进行聊天补全
    async def chat_completion(self, messages: list, model: str, temperature=0.7, top_p=0.9, max_tokens=None, 
                              frequency_penalty=0.0, presence_penalty=0.0, stop=None) -> str:
        # 验证输入
        if not messages or not isinstance(messages, list):
            logger.error("Moonshot请求错误: 消息列表为空或格式不正确")
            raise ValueError("消息列表为空或格式不正确")
            
        if not model or not isinstance(model, str):
            logger.error("Moonshot请求错误: 模型名称无效")
            raise ValueError("模型名称无效")
            
        # 验证消息格式
        valid_messages = []
        for msg in messages:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                logger.warning(f"跳过无效消息格式: {msg}")
                continue
                
            # Moonshot支持OpenAI风格的角色(user/assistant/system)
            role = msg['role']
            if role not in ['user', 'assistant', 'system']:
                logger.warning(f"将未知角色 '{role}' 转换为 'user'")
                role = 'user'
                
            valid_messages.append({
                "role": role,
                "content": msg['content']
            })
            
        if not valid_messages:
            logger.error("Moonshot请求错误: 转换后的消息列表为空")
            raise ValueError("转换后的消息列表为空")
        
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "model": model,  # 模型名称
                "messages": valid_messages,  # 消息列表
                "temperature": temperature,  # 温度参数
                "top_p": top_p,  # Top-p参数
                "stream": False  # 不使用流式传输
            }
            
            # 添加可选参数
            if max_tokens is not None and max_tokens > 0:
                payload["max_tokens"] = max_tokens
                
            if frequency_penalty != 0:
                payload["frequency_penalty"] = frequency_penalty
                
            if presence_penalty != 0:
                payload["presence_penalty"] = presence_penalty
                
            if stop and (isinstance(stop, str) or isinstance(stop, list)):
                payload["stop"] = stop
            
            try:
                logger.debug(f"向Moonshot发送请求: {model}, 消息数: {len(valid_messages)}")
                
                # 发送 POST 请求到 Moonshot 的 /v1/chat/completions 接口
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(60)  # 添加超时设置
                ) as response:
                    response_text = await response.text()
                    
                    # 检查响应状态码
                    if response.status != 200:
                        logger.error(f"Moonshot请求失败，状态码: {response.status}，详情: {response_text}")
                        raise Exception(f"Moonshot API请求失败: {response.status} - {response_text}")
                    
                    # 解析 JSON 响应
                    try:
                        result = await response.json()
                    except Exception as e:
                        logger.error(f"Moonshot响应JSON解析失败: {str(e)}, 原始响应: {response_text}")
                        raise ValueError(f"无法解析Moonshot API响应: {str(e)}")
                    
                    # 验证响应格式
                    if not result or 'choices' not in result or not result['choices']:
                        logger.error(f"Moonshot响应格式无效: {result}")
                        raise ValueError("Moonshot响应格式无效，缺少choices字段")
                    
                    # 返回聊天补全结果
                    choice = result['choices'][0]
                    if 'message' not in choice or 'content' not in choice['message']:
                        logger.error(f"Moonshot响应格式异常: {choice}")
                        raise ValueError("Moonshot响应格式无效，缺少message.content")
                    
                    # 记录使用信息（如果存在）
                    if 'usage' in result:
                        logger.debug(f"Moonshot API使用情况: 输入tokens: {result['usage'].get('prompt_tokens', '未知')}, "
                                   f"输出tokens: {result['usage'].get('completion_tokens', '未知')}")
                    
                    return choice['message']['content']
                    
            except aiohttp.ClientError as e:
                # 捕获 aiohttp 客户端错误
                logger.error(f"Moonshot请求客户端错误: {str(e)}")
                raise
            except Exception as e:
                # 捕获其他未知异常并记录错误日志
                logger.error(f"Moonshot请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 ZhipuAdapter 类，继承自 BaseAdapter
class ZhipuAdapter(BaseAdapter):
    # 构造函数，初始化智谱 API 密钥和基准 URL
    def __init__(self, api_key: str, base_url="https://open.bigmodel.cn"):
        if not api_key or not isinstance(api_key, str):
            raise ValueError("智谱 API Key不能为空且必须是字符串")
            
        self.base_url = base_url
        self.api_key = api_key
        
        # 解析API密钥（智谱API密钥格式通常为"id.secret"）
        try:
            self.api_id, self.api_secret = api_key.split('.')
            logger.debug("已成功解析智谱API密钥")
        except ValueError:
            logger.warning("智谱API密钥格式不正确，应为'id.secret'格式")
            self.api_id = api_key
            self.api_secret = ""
            
        logger.debug(f"已初始化智谱适配器，API基础URL: {base_url}")
        
    # 生成JWT令牌，用于API认证
    def _generate_token(self, expiration_seconds=3600):
        """生成JWT令牌用于智谱API认证
        
        Args:
            expiration_seconds: 令牌有效期，默认3600秒
            
        Returns:
            str: JWT令牌
        """
        try:
            # 尝试导入jwt，如果失败则使用备用方案
            try:
                import jwt
            except ImportError:
                logger.warning("PyJWT库未安装，将使用备用认证方式")
                return self.api_key
                
            import time
            import uuid
            
            # 当前时间戳（秒）
            iat = int(time.time())
            # 过期时间戳
            exp = iat + expiration_seconds
            # 负载数据
            payload = {
                "api_key": self.api_id,
                "exp": exp,
                "timestamp": iat,
                "uuid": str(uuid.uuid4())  # 随机UUID，防止重放攻击
            }
            
            # 使用HS256算法和API密钥的secret部分签名
            token = jwt.encode(
                payload,
                self.api_secret,
                algorithm="HS256"
            )
            
            return token
        except Exception as e:
            logger.error(f"生成智谱API令牌失败: {str(e)}")
            # 如果生成令牌失败，返回原始API密钥
            return self.api_key

    # 实现 chat_completion 抽象方法，用于与智谱服务进行聊天补全
    async def chat_completion(self, messages: list, model: str, temperature=0.7, top_p=0.7, max_tokens=1024) -> str:
        # 验证输入
        if not messages or not isinstance(messages, list):
            logger.error("智谱请求错误: 消息列表为空或格式不正确")
            raise ValueError("消息列表为空或格式不正确")
            
        if not model or not isinstance(model, str):
            logger.error("智谱请求错误: 模型名称无效")
            raise ValueError("模型名称无效")
            
        # 验证消息格式
        valid_messages = []
        for msg in messages:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                logger.warning(f"跳过无效消息格式: {msg}")
                continue
                
            # 角色映射（智谱API支持的角色是user/assistant）
            role = msg['role']
            if role not in ['user', 'assistant']:
                if role == 'system':
                    # 将system消息作为user消息处理
                    role = 'user'
                    logger.warning("智谱API不直接支持system角色，已转换为user角色")
                else:
                    logger.warning(f"将未知角色 '{role}' 转换为 'user'")
                    role = 'user'
                    
            valid_messages.append({
                "role": role,
                "content": msg['content']
            })
            
        if not valid_messages:
            logger.error("智谱请求错误: 转换后的消息列表为空")
            raise ValueError("转换后的消息列表为空")
            
        # 生成JWT令牌
        try:
            token = self._generate_token()
            # 设置请求头，包含授权信息和内容类型
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
        except Exception as e:
            # 如果生成令牌失败，尝试使用原始API密钥作为令牌
            logger.warning(f"生成JWT令牌失败，将使用原始API密钥: {str(e)}")
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 构建请求体 payload
            payload = {
                "model": model,  # 模型名称
                "messages": valid_messages,  # 消息列表
                "temperature": temperature,  # 温度参数
                "top_p": top_p,  # Top-p参数
                "max_tokens": max_tokens,  # 最大生成token数
                "stream": False  # 不使用流式传输
            }
            
            try:
                logger.debug(f"向智谱发送请求: {model}, 消息数: {len(valid_messages)}")
                
                # 发送 POST 请求到智谱的API接口
                # 智谱API有两种可能的端点，根据模型名称选择
                if 'chatglm' in model.lower():
                    api_url = f"{self.base_url}/api/paas/v3/model-api/{model}/sse-invoke"
                else:
                    api_url = f"{self.base_url}/api/paas/v4/chat/completions"
                    
                logger.debug(f"智谱API请求URL: {api_url}")
                
                async with session.post(
                    api_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(60)  # 添加超时设置
                ) as response:
                    response_text = await response.text()
                    
                    # 检查响应状态码
                    if response.status != 200:
                        logger.error(f"智谱请求失败，状态码: {response.status}，详情: {response_text}")
                        raise Exception(f"智谱API请求失败: {response.status} - {response_text}")
                    
                    # 解析 JSON 响应
                    try:
                        result = await response.json()
                    except Exception as e:
                        logger.error(f"智谱响应JSON解析失败: {str(e)}, 原始响应: {response_text}")
                        raise ValueError(f"无法解析智谱API响应: {str(e)}")
                    
                    # 检查错误信息
                    if 'code' in result and result['code'] != 0:
                        error_msg = result.get('msg', '未知错误')
                        logger.error(f"智谱API返回错误: {result['code']} - {error_msg}")
                        raise Exception(f"智谱API返回错误: {result['code']} - {error_msg}")
                    
                    # 检查响应格式并提取内容
                    if 'data' in result and 'choices' in result['data'] and result['data']['choices']:
                        choice = result['data']['choices'][0]
                        if 'message' in choice and 'content' in choice['message']:
                            return choice['message']['content']
                    
                    # 兼容v3版本API的返回格式
                    if 'choices' in result and result['choices']:
                        choice = result['choices'][0]
                        if 'message' in choice and 'content' in choice['message']:
                            return choice['message']['content']
                        
                    # 记录使用信息（如果存在）
                    if 'usage' in result:
                        logger.debug(f"智谱API使用情况: 输入tokens: {result['usage'].get('prompt_tokens', '未知')}, "
                                   f"输出tokens: {result['usage'].get('completion_tokens', '未知')}")
                        
                    logger.error(f"无法从智谱响应中提取文本内容: {result}")
                    return ""
                    
            except aiohttp.ClientError as e:
                # 捕获 aiohttp 客户端错误
                logger.error(f"智谱请求客户端错误: {str(e)}")
                raise
            except Exception as e:
                # 捕获其他未知异常并记录错误日志
                logger.error(f"智谱请求失败: {str(e)}")
                # 重新抛出异常
                raise

# 定义 SparkAdapter 类，继承自 BaseAdapter
class SparkAdapter(BaseAdapter):
    # 构造函数，初始化 Spark API 凭据和基准 URL
    def __init__(self, api_key: str, app_id: Optional[str] = None, api_secret: Optional[str] = None, base_url="https://spark-api.xf-yun.com"):
        if not api_key or not isinstance(api_key, str):
            raise ValueError("讯飞星火 API Key不能为空且必须是字符串")
            
        self.base_url = base_url
        
        # 讯飞星火API支持两种认证方式：
        # 1. Bearer Token认证 (api_key)
        # 2. 三元组认证 (app_id, api_key, api_secret)
        self.use_token_auth = True
        self.api_key = api_key
        
        if app_id and api_secret:
            self.use_token_auth = False
            self.app_id = app_id
            self.api_secret = api_secret
            logger.debug("使用讯飞星火API三元组认证方式")
        else:
            logger.debug("使用讯飞星火API Token认证方式")
        
        logger.debug(f"已初始化讯飞星火适配器，API基础URL: {base_url}")
        
    # 生成请求头，包括认证信息
    def _get_headers(self):
        """根据认证方式生成请求头"""
        if self.use_token_auth:
            # Token认证方式
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        else:
            # 三元组认证方式，需要生成签名
            try:
                import time
                import hmac
                import base64
                import hashlib
                
                # 当前时间戳（秒）
                current_time = int(time.time())
                # 随机字符串，这里使用时间戳
                nonce = str(current_time)
                
                # 构建签名原文: app_id + nonce + timestamp
                signature_origin = f"{self.app_id}{nonce}{current_time}"
                
                # 使用HMAC-SHA256算法，api_secret作为密钥计算签名
                signature = hmac.new(
                    self.api_secret.encode('utf-8'),
                    signature_origin.encode('utf-8'),
                    digestmod=hashlib.sha256
                ).digest()
                
                # Base64编码签名结果
                signature_base64 = base64.b64encode(signature).decode('utf-8')
                
                # 构建认证头
                authorization = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_base64}"'
                
                return {
                    "Authorization": authorization,
                    "Content-Type": "application/json",
                    "X-Appid": self.app_id,
                    "X-Timestamp": str(current_time),
                    "X-Nonce": nonce
                }
            except Exception as e:
                logger.error(f"生成讯飞星火API认证头失败: {str(e)}")
                # 如果签名生成失败，回退到简单的token认证
                return {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

    # 实现 chat_completion 抽象方法，用于与 Spark 服务进行聊天补全
    async def chat_completion(self, messages: list, model: str, temperature=0.7, top_k=4, max_tokens=2048) -> str:
        # 验证输入
        if not messages or not isinstance(messages, list):
            logger.error("讯飞星火请求错误: 消息列表为空或格式不正确")
            raise ValueError("消息列表为空或格式不正确")
            
        if not model or not isinstance(model, str):
            logger.error("讯飞星火请求错误: 模型名称无效")
            raise ValueError("模型名称无效")
            
        # 验证消息格式
        valid_messages = []
        for msg in messages:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                logger.warning(f"跳过无效消息格式: {msg}")
                continue
                
            # 角色映射（讯飞星火API支持的角色是user/assistant/system）
            role = msg['role']
            if role not in ['user', 'assistant', 'system']:
                logger.warning(f"将未知角色 '{role}' 转换为 'user'")
                role = 'user'
                
            valid_messages.append({
                "role": role,
                "content": msg['content']
            })
            
        if not valid_messages:
            logger.error("讯飞星火请求错误: 转换后的消息列表为空")
            raise ValueError("转换后的消息列表为空")
        
        # 获取请求头，包含认证信息
        headers = self._get_headers()
        
        # 使用 aiohttp.ClientSession 创建一个异步 HTTP 客户端会话
        async with aiohttp.ClientSession() as session:
            # 确定API版本和端点
            api_version = "v3.5"  # 默认版本
            if "v2" in model:
                api_version = "v2.1"
            elif "v3" in model:
                api_version = "v3.5"
            elif "v4" in model:
                api_version = "v4.0"
                
            # 讯飞星火API不在URL中包含模型名称，而是在payload中指定
            # 提取模型编号，例如从"spark-v3"中提取"3"
            model_version = ''.join(filter(str.isdigit, model))
            spark_api_model = f"spark-{model_version}" if model_version else model
                
            # 构建请求体 payload
            payload = {
                "header": {
                    "app_id": getattr(self, "app_id", ""),  # 如果使用三元组认证，提供app_id
                    "uid": f"user_{int(time.time())}"  # 用户ID，这里使用时间戳
                },
                "parameter": {
                    "chat": {
                        "domain": spark_api_model,  # 模型版本
                        "temperature": temperature,  # 温度参数
                        "top_k": top_k,  # Top-k参数
                        "max_tokens": max_tokens,  # 最大生成token数
                        "auditing": "default"  # 审核设置，使用默认值
                    }
                },
                "payload": {
                    "message": {
                        "text": valid_messages  # 消息列表
                    }
                }
            }
            
            try:
                logger.debug(f"向讯飞星火发送请求: {spark_api_model}, API版本: {api_version}, 消息数: {len(valid_messages)}")
                
                # 发送 POST 请求到 Spark API
                api_url = f"{self.base_url}/{api_version}/chat"
                
                async with session.post(
                    api_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(60)  # 添加超时设置
                ) as response:
                    response_text = await response.text()
                    
                    # 检查响应状态码
                    if response.status != 200:
                        logger.error(f"讯飞星火请求失败，状态码: {response.status}，详情: {response_text}")
                        raise Exception(f"讯飞星火API请求失败: {response.status} - {response_text}")
                    
                    # 解析 JSON 响应
                    try:
                        result = await response.json()
                    except Exception as e:
                        logger.error(f"讯飞星火响应JSON解析失败: {str(e)}, 原始响应: {response_text}")
                        raise ValueError(f"无法解析讯飞星火API响应: {str(e)}")
                    
                    # 检查响应码
                    header = result.get('header', {})
                    code = header.get('code', -1)
                    
                    if code != 0:
                        error_msg = header.get('message', '未知错误')
                        logger.error(f"讯飞星火API返回错误: {code} - {error_msg}")
                        raise Exception(f"讯飞星火API返回错误: {code} - {error_msg}")
                    
                    # 解析响应文本
                    payload = result.get('payload', {})
                    choices = payload.get('choices', {})
                    text = choices.get('text', [])
                    
                    if not text:
                        logger.error(f"讯飞星火响应中没有文本内容: {result}")
                        return ""
                    
                    # 讯飞星火API可能返回多个消息，找到assistant角色的消息
                    for msg in text:
                        if msg.get('role') == 'assistant':
                            return msg.get('content', '')
                    
                    # 如果没有找到assistant消息，返回最后一个消息
                    if text and 'content' in text[-1]:
                        return text[-1]['content']
                    
                    # 使用兼容格式
                    if 'choices' in result and result['choices']:
                        choice = result['choices'][0]
                        if 'message' in choice and 'content' in choice['message']:
                            return choice['message']['content']
                    
                    # 记录使用信息（如果存在）
                    usage = result.get('usage', {})
                    if usage:
                        logger.debug(f"讯飞星火API使用情况: 输入tokens: {usage.get('prompt_tokens', '未知')}, "
                                   f"输出tokens: {usage.get('completion_tokens', '未知')}")
                    
                    logger.error(f"无法从讯飞星火响应中提取文本内容: {result}")
                    return ""
                    
            except aiohttp.ClientError as e:
                # 捕获 aiohttp 客户端错误
                logger.error(f"讯飞星火请求客户端错误: {str(e)}")
                raise
            except Exception as e:
                # 捕获其他未知异常并记录错误日志
                logger.error(f"讯飞星火请求失败: {str(e)}")
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