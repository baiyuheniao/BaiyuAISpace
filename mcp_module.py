import logging
from typing import Dict, Any
from api_adapter import BaseAdapter

logger = logging.getLogger(__name__)

class MCP:
    def __init__(self):
        self.providers: Dict[str, BaseAdapter] = {}
        self.current_provider: str = None
        self.configurations: Dict[str, Dict] = {}
        
    def save_configuration(self, name: str, config: Dict[str, Any]):
        """保存提供商配置"""
        self.configurations[name] = config
        
    def get_configuration(self, name: str) -> Dict[str, Any]:
        """获取已保存的配置"""
        return self.configurations.get(name, {})

    def add_provider(self, name: str, config: Dict[str, Any]):
        """注册新的LLM服务提供商"""
        name_lower = name.lower()
        
        if name_lower == 'openai':
            self.providers[name] = OpenAIAdapter(**config)
        elif name_lower == 'anthropic':
            self.providers[name] = AnthropicAdapter(**config)
        elif name_lower == 'meta':
            self.providers[name] = MetaAdapter(**config)
        elif name_lower == 'google':
            self.providers[name] = GoogleAdapter(**config)
        elif name_lower == 'cohere':
            self.providers[name] = CohereAdapter(**config)
        elif name_lower == 'replicate':
            self.providers[name] = ReplicateAdapter(**config)
        elif name_lower == '阿里云':
            self.providers[name] = AliyunAdapter(**config)
        elif name_lower == '智谱':
            self.providers[name] = ZhipuAdapter(**config)
        elif name_lower == 'mistral':
            self.providers[name] = MistralAdapter(**config)
        elif name_lower == 'deepseek':
            self.providers[name] = DeepSeekAdapter(**config)
        elif name_lower == 'lambda labs':
            self.providers[name] = LambdaLabsAdapter(**config)
        elif name_lower == '硅基流动':
            self.providers[name] = SiliconFlowAdapter(**config)
        elif name_lower == '其他':
            self.providers[name] = OtherAdapter(**config)
        else:
            raise ValueError(f"不支持的提供商类型: {name}")

    def switch_current_provider(self, name: str):
        """切换当前使用的LLM服务"""
        if name not in self.providers:
            raise KeyError(f"未注册的提供商: {name}")
        self.current_provider = name
        logger.info(f"已切换到LLM服务提供商: {name}")

    async def handle_request(self, messages: list, model: str) -> str:
        """处理聊天请求并路由到当前提供商"""
        if not self.current_provider:
            raise RuntimeError("未选择LLM服务提供商")
        
        provider = self.providers.get(self.current_provider)
        if not provider:
            raise RuntimeError(f"无效的当前提供商: {self.current_provider}")

        try:
            return await provider.chat_completion(messages, model)
        except Exception as e:
            logger.error(f"LLM请求处理失败: {str(e)}")
            raise

    def export_configuration(self) -> Dict[str, Any]:
        """导出所有MCP配置"""
        return self.configurations

    def import_configuration(self, config: Dict[str, Any]):
        """导入MCP配置"""
        if not isinstance(config, dict):
            raise ValueError("导入的配置必须是字典格式")
        self.configurations.update(config)
        logger.info("MCP配置已成功导入")