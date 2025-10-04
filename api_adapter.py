"""
This file is part of BaiyuAISpace.
"""

from abc import ABC, abstractmethod
import aiohttp
import logging
import time
import json
from typing import Optional, List, Union
import asyncio
import mimetypes

logger = logging.getLogger(__name__)

def _extract_text_from_response(result):
    """
    尝试从不同的返回格式中提取文本回复，兼容多家API常见格式。
    返回：字符串（如果无法提取则返回空字符串）
    """
    if not result:
        return ""
    try:
        if isinstance(result.get("choices"), list) and result["choices"]:
            choice = result["choices"][0]
            if isinstance(choice, dict):
                msg = choice.get("message")
                if msg and isinstance(msg, dict) and "content" in msg:
                    return msg["content"]
                if "content" in choice and isinstance(choice["content"], str):
                    return choice["content"]
                if "text" in choice and isinstance(choice["text"], str):
                    return choice["text"]
    except Exception:
        pass
    if "result" in result:
        r = result["result"]
        if isinstance(r, str):
            return r
        if isinstance(r, dict):
            if "content" in r and isinstance(r["content"], str):
                return r["content"]
            if isinstance(r.get("choices"), list) and r["choices"]:
                c = r["choices"][0]
                if isinstance(c, dict) and "content" in c and isinstance(c["content"], str):
                    return c["content"]
    if "output" in result:
        out = result["output"]
        if isinstance(out, str):
            return out
        if isinstance(out, list) and out:
            for it in out:
                if isinstance(it, str):
                    return it
                if isinstance(it, dict) and "text" in it:
                    return it["text"]
    if "candidates" in result and isinstance(result["candidates"], list) and result["candidates"]:
        cand = result["candidates"][0]
        if isinstance(cand, dict):
            content = cand.get("content")
            if isinstance(content, dict) and "parts" in content and content["parts"]:
                parts = content["parts"]
                if isinstance(parts[0], dict) and "text" in parts[0]:
                    return parts[0]["text"]
            if isinstance(content, str):
                return content
    try:
        def find_str(obj):
            if isinstance(obj, str):
                return obj
            if isinstance(obj, dict):
                for v in obj.values():
                    res = find_str(v)
                    if res:
                        return res
            if isinstance(obj, list):
                for v in obj:
                    res = find_str(v)
                    if res:
                        return res
            return ""
        return find_str(result) or ""
    except Exception:
        return ""

class BaseAdapter(ABC):
    @abstractmethod
    async def chat_completion(self, messages: list, model: str) -> str:
        pass

class OllamaAdapter(BaseAdapter):
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url

    async def chat_completion(self, messages: list, model: str) -> str:
        if not messages or not isinstance(messages, list):
            logger.error("Ollama请求错误: 消息列表为空或格式不正确")
            raise ValueError("消息列表为空或格式不正确")
        if not model or not isinstance(model, str):
            logger.error("Ollama请求错误: 模型名称无效")
            raise ValueError("模型名称无效")
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            try:
                logger.debug(f"向Ollama发送请求: {model}, 消息数: {len(messages)}")
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(60)
                ) as response:
                    response_text = await response.text()
                    if response.status != 200:
                        logger.error(f"Ollama请求失败，状态码: {response.status}，详情: {response_text}")
                        raise Exception(f"Ollama API请求失败: {response.status} - {response_text}")
                    try:
                        result = await response.json()
                    except Exception as e:
                        logger.error(f"Ollama响应JSON解析失败: {str(e)}, 原始响应: {response_text}")
                        raise ValueError(f"无法解析Ollama API响应: {str(e)}")
                    if 'message' in result and 'content' in result['message']:
                        return result['message']['content']
                    logger.error(f"无法从Ollama响应中提取文本内容: {result}")
                    return ""
            except aiohttp.ClientError as e:
                logger.error(f"Ollama请求客户端错误: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Ollama请求失败: {str(e)}")
                raise

class SiliconFlowAdapter(BaseAdapter):
    def __init__(self, api_key: str, base_url: str = "https://api.siliconflow.cn"):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        print(f"SiliconFlowAdapter初始化: base_url={self.base_url}")

    async def chat_completion(self, messages: list, model: str, **kwargs) -> str:
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            if 'temperature' in kwargs:
                payload['temperature'] = kwargs['temperature']
            if 'max_tokens' in kwargs:
                payload['max_tokens'] = kwargs['max_tokens']
            if 'top_p' in kwargs:
                payload['top_p'] = kwargs['top_p']
            if 'top_k' in kwargs:
                payload['top_k'] = kwargs['top_k']
            if self.base_url.endswith('/v1'):
                api_url = f"{self.base_url}/chat/completions"
            else:
                api_url = f"{self.base_url}/v1/chat/completions"
            print(f"SiliconFlowAdapter请求URL: {api_url}")
            print(f"SiliconFlowAdapter请求payload: {payload}")
            try:
                async with session.post(
                    api_url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(60)
                ) as response:
                    response_text = await response.text()
                    if response.status != 200:
                        logger.error(f"硅基流动请求失败，状态码: {response.status}，详情: {response_text}")
                        try:
                            error_data = await response.json()
                            if 'message' in error_data:
                                error_msg = error_data['message']
                                if 'Model does not exist' in error_msg or 'model does not exist' in error_msg:
                                    raise ValueError(f"模型 '{model}' 不存在，请检查模型名称是否正确。错误详情: {error_msg}")
                                else:
                                    raise Exception(f"硅基流动API请求失败: {response.status} - {error_msg}")
                            else:
                                raise Exception(f"硅基流动API请求失败: {response.status} - {response_text}")
                        except Exception as parse_error:
                            raise Exception(f"硅基流动API请求失败: {response.status} - {response_text}")
                    try:
                        result = await response.json()
                    except Exception as e:
                        logger.error(f"硅基流动响应JSON解析失败: {str(e)}, 原始响应: {response_text}")
                        raise ValueError(f"无法解析硅基流动API响应: {str(e)}")
                    text = _extract_text_from_response(result)
                    if not text:
                        logger.error(f"硅基流动响应格式无效或无法提取文本: {result}")
                        raise ValueError("硅基流动响应格式无效，无法提取文本")
                    if 'usage' in result:
                        logger.debug(f"硅基流动API使用情况: 输入tokens: {result['usage'].get('prompt_tokens', '未知')}, 输出tokens: {result['usage'].get('completion_tokens', '未知')}")
                    return text
            except aiohttp.ClientError as e:
                logger.error(f"硅基流动请求客户端错误: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"硅基流动请求失败: {str(e)}")
                raise
# ... (其余适配器保持不变) ...# END FILE api_adapter.py