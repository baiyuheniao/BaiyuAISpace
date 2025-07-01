# This file is part of BaiyuAISpace.
# Copyright (C) 2025 白Bai_YU雨
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.




# 导入 logging 模块，用于日志记录
import logging
# 从 typing 模块导入 Dict 和 Any，用于类型提示
from typing import Dict, Any, Optional, List
# 从 api_adapter 模块导入 BaseAdapter，用于继承
from api_adapter import BaseAdapter, OllamaAdapter, OpenAIAdapter, AnthropicAdapter, MetaAdapter, GoogleAdapter, CohereAdapter, ReplicateAdapter, AliyunAdapter, BaiduAdapter, DeepSeekAdapter, MoonshotAdapter, ZhipuAdapter, SparkAdapter, MinimaxAdapter, SenseChatAdapter, XunfeiAdapter, CustomAdapter, SiliconFlowAdapter
import json
import os

# 获取一个 logger 实例，用于记录日志
logger = logging.getLogger(__name__)

# 定义 MCP 类，用于管理 LLM 服务提供商
class MCP:
    # 构造函数，初始化提供商字典、当前提供商名称和配置字典
    def __init__(self, config_file="mcp_config.json"):
        self.providers: Dict[str, BaseAdapter] = {}  # 存储 LLM 服务提供商实例
        self.current_provider: Optional[str] = None  # 当前使用的 LLM 服务提供商名称
        self.configurations: Dict[str, Dict] = {}  # 存储提供商的配置信息
        self.config_file = config_file  # 配置文件路径
        
        # 确保配置目录存在
        self._ensure_config_dir()
        
        # 加载保存的配置
        self.load_configurations()
        
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        config_dir = os.path.dirname(self.config_file)
        if config_dir and not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir, exist_ok=True)
                print(f"创建配置目录: {config_dir}")
            except Exception as e:
                print(f"创建配置目录失败: {str(e)}")
    
    def set_config_file(self, config_file: str):
        """设置配置文件路径"""
        self.config_file = config_file
        self._ensure_config_dir()
        # 重新加载配置
        self.load_configurations()
        
    def load_configurations(self):
        """从文件加载配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.configurations = data.get('configurations', {})
                    self.current_provider = data.get('current_provider')
                    print(f"已加载配置: {len(self.configurations)} 个提供商")
                    if self.current_provider:
                        print(f"当前提供商: {self.current_provider}")
            else:
                print("配置文件不存在，将创建新的配置")
        except Exception as e:
            print(f"加载配置失败: {str(e)}")
            self.configurations = {}
            self.current_provider = None
    
    def save_configurations(self):
        """保存配置到文件"""
        try:
            data = {
                'configurations': self.configurations,
                'current_provider': self.current_provider
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"配置已保存到: {self.config_file}")
        except Exception as e:
            print(f"保存配置失败: {str(e)}")
        
    # 保存提供商配置的方法
    def save_configuration(self, name: str, config: Dict[str, Any]):
        """保存提供商配置"""
        self.configurations[name] = config
        self.save_configurations()
        
    # 获取已保存配置的方法
    def get_configuration(self, name: str) -> Dict[str, Any]:
        """获取已保存的配置"""
        return self.configurations.get(name, {})
    
    # 获取所有已保存配置的方法
    def get_all_configurations(self) -> Dict[str, Dict[str, Any]]:
        """获取所有已保存的配置"""
        return self.configurations.copy()

    # 添加提供商的方法
    def add_provider(self, name: str, config: Dict[str, Any]):
        """注册新的LLM服务提供商"""
        print(f"正在添加提供商: {name}")
        name_lower = name.lower()
        
        # 提取构造函数需要的参数
        constructor_params = {}
        if 'api_key' in config:
            constructor_params['api_key'] = config['api_key']
        if 'base_url' in config:
            constructor_params['base_url'] = config['base_url']
        if 'organization_id' in config:
            constructor_params['organization_id'] = config['organization_id']
        if 'api_version' in config:
            constructor_params['api_version'] = config['api_version']
        if 'secret_key' in config:
            constructor_params['secret_key'] = config['secret_key']
        if 'app_id' in config:
            constructor_params['app_id'] = config['app_id']
        if 'api_secret' in config:
            constructor_params['api_secret'] = config['api_secret']
        
        print(f"构造参数: {constructor_params}")
        
        # 根据提供商名称创建相应的适配器实例
        if name_lower == 'ollama':
            self.providers[name] = OllamaAdapter(**constructor_params)
        elif name_lower == 'openai':
            self.providers[name] = OpenAIAdapter(**constructor_params)
        elif name_lower == 'anthropic':
            self.providers[name] = AnthropicAdapter(**constructor_params)
        elif name_lower == 'meta':
            self.providers[name] = MetaAdapter(**constructor_params)
        elif name_lower == 'google':
            self.providers[name] = GoogleAdapter(**constructor_params)
        elif name_lower == 'cohere':
            self.providers[name] = CohereAdapter(**constructor_params)
        elif name_lower == 'replicate':
            self.providers[name] = ReplicateAdapter(**constructor_params)
        elif name_lower == 'aliyun' or name == '阿里云':
            print(f"创建阿里云适配器: {name}")
            self.providers[name] = AliyunAdapter(**constructor_params)
        elif name_lower == 'baidu':
            self.providers[name] = BaiduAdapter(**constructor_params)
        elif name_lower == 'deepseek':
            self.providers[name] = DeepSeekAdapter(**constructor_params)
        elif name_lower == 'moonshot':
            self.providers[name] = MoonshotAdapter(**constructor_params)
        elif name_lower == 'zhipu' or name == '智谱':
            print(f"创建智谱适配器: {name}")
            self.providers[name] = ZhipuAdapter(**constructor_params)
        elif name_lower == 'spark':
            self.providers[name] = SparkAdapter(**constructor_params)
        elif name_lower == 'minimax':
            self.providers[name] = MinimaxAdapter(**constructor_params)
        elif name_lower == 'sensechat':
            self.providers[name] = SenseChatAdapter(**constructor_params)
        elif name_lower == 'xunfei':
            self.providers[name] = XunfeiAdapter(**constructor_params)
        elif name_lower == 'custom' or name == '其他':
            print(f"创建自定义适配器: {name}")
            # 为自定义提供商提供默认的base_url
            if 'base_url' not in constructor_params:
                constructor_params['base_url'] = "https://api.example.com"  # 默认URL，用户需要根据实际情况修改
            self.providers[name] = CustomAdapter(**constructor_params)
        elif name == '硅基流动':
            print(f"创建硅基流动适配器: {name}")
            # 为硅基流动提供默认的base_url
            if 'base_url' not in constructor_params:
                constructor_params['base_url'] = "https://api.siliconflow.cn"
            self.providers[name] = SiliconFlowAdapter(**constructor_params)
        else:
            # 如果是不支持的提供商类型，则抛出 ValueError 异常
            print(f"不支持的提供商类型: {name}")
            raise ValueError(f"不支持的提供商类型: {name}")
        
        print(f"提供商 {name} 添加成功")

    # 切换当前使用的 LLM 服务的方法
    def switch_current_provider(self, name: str):
        """切换当前使用的LLM服务"""
        # 检查提供商是否已注册
        if name not in self.providers:
            raise KeyError(f"未注册的提供商: {name}")
        self.current_provider = name  # 设置当前提供商
        self.save_configurations()  # 保存配置
        logger.info(f"已切换到LLM服务提供商: {name}")  # 记录日志

    # 处理聊天请求并路由到当前提供商的方法
    async def handle_request(self, messages: list, model: str, file_urls: Optional[list] = None) -> str:
        """处理聊天请求并路由到当前提供商"""
        print(f"处理聊天请求: 当前提供商={self.current_provider}, 传入模型={model}, 文件数={len(file_urls) if file_urls else 0}")
        
        # 检查是否已选择 LLM 服务提供商
        if not self.current_provider:
            raise RuntimeError("未选择LLM服务提供商")
        
        # 获取当前提供商实例
        provider = self.providers.get(self.current_provider)
        if not provider:
            raise RuntimeError(f"无效的当前提供商: {self.current_provider}")

        # 获取保存的配置参数
        saved_config = self.configurations.get(self.current_provider, {})
        print(f"保存的配置: {saved_config}")
        
        # 使用配置中保存的模型名称，如果没有则使用传入的模型名称
        actual_model = saved_config.get('model', model)
        print(f"实际使用的模型: {actual_model}")
        print(f"模型名称类型: {type(actual_model)}")
        
        # 检查模型名称是否为空或无效
        if not actual_model or not str(actual_model).strip():
            raise ValueError(f"模型名称无效: '{actual_model}'，请在设置页面配置正确的模型名称")
        
        # 提取聊天参数
        chat_params = {}
        if 'temperature' in saved_config:
            chat_params['temperature'] = saved_config['temperature']
        if 'top_k' in saved_config:
            chat_params['top_k'] = saved_config['top_k']
        if 'max_tokens' in saved_config:
            chat_params['max_tokens'] = saved_config['max_tokens']
        if 'top_p' in saved_config:
            chat_params['top_p'] = saved_config['top_p']

        print(f"聊天参数: {chat_params}")

        # 多模态支持列表（可根据实际扩展）
        multimodal_providers = {
            'openai': ['gpt-4-vision-preview', 'gpt-4o', 'gpt-4v'],
            'zhipu': ['glm-4v', 'glm-4v-32k'],
            'aliyun': ['qwen-vl-plus', 'qwen-vl-max'],
            'baidu': ['ernie-vil', 'ernie-bot-multimodal'],
            'google': ['gemini-1.5-pro', 'gemini-1.5-flash'],
            # ...可扩展
        }
        provider_key = str(self.current_provider).lower()
        model_key = str(model).lower()
        # 检查多模态支持
        if file_urls:
            support = False
            if provider_key in multimodal_providers:
                for m in multimodal_providers[provider_key]:
                    if m in model_key:
                        support = True
                        break
            if not support:
                logger.error(f"多模态请求被拒绝：当前模型不支持多模态，provider={provider_key}, model={model_key}, file_urls={file_urls}")
                raise ValueError(f"当前模型({self.current_provider}/{model})暂不支持图片/视频输入，请切换支持多模态的模型。")

        try:
            extra_params = chat_params.copy()
            if file_urls is not None and isinstance(file_urls, list):
                extra_params['file_urls'] = file_urls
            result = await provider.chat_completion(messages, actual_model, **extra_params)
            print(f"聊天请求处理成功，响应长度: {len(result)}")
            return result
        except Exception as e:
            # 捕获异常并记录错误日志
            print(f"LLM请求处理失败: {str(e)}")
            logger.error(f"LLM请求处理失败: {str(e)}")
            # 重新抛出异常
            raise

    # 导出所有 MCP 配置的方法
    def export_configuration(self) -> Dict[str, Any]:
        """导出所有MCP配置"""
        return self.configurations

    # 导入 MCP 配置的方法
    def import_configuration(self, config: Dict[str, Any]):
        """导入MCP配置"""
        # 检查导入的配置是否为字典格式
        if not isinstance(config, dict):
            raise ValueError("导入的配置必须是字典格式")
        self.configurations.update(config)  # 更新配置
        self.save_configurations()  # 保存配置
        logger.info("MCP配置已成功导入")  # 记录日志
