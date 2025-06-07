# 导入 logging 模块，用于日志记录
import logging
# 从 typing 模块导入 Dict 和 Any，用于类型提示
from typing import Dict, Any
# 从 api_adapter 模块导入 BaseAdapter，用于继承
from api_adapter import BaseAdapter, OllamaAdapter, OpenAIAdapter, AnthropicAdapter, MetaAdapter, GoogleAdapter, CohereAdapter, ReplicateAdapter, AliyunAdapter, BaiduAdapter, DeepSeekAdapter, MoonshotAdapter, ZhipuAdapter, SparkAdapter, MinimaxAdapter, SenseChatAdapter, XunfeiAdapter, CustomAdapter

# 获取一个 logger 实例，用于记录日志
logger = logging.getLogger(__name__)

# 定义 MCP 类，用于管理 LLM 服务提供商
class MCP:
    # 构造函数，初始化提供商字典、当前提供商名称和配置字典
    def __init__(self):
        self.providers: Dict[str, BaseAdapter] = {}  # 存储 LLM 服务提供商实例
        self.current_provider: str = None  # 当前使用的 LLM 服务提供商名称
        self.configurations: Dict[str, Dict] = {}  # 存储提供商的配置信息
        
    # 保存提供商配置的方法
    def save_configuration(self, name: str, config: Dict[str, Any]):
        """保存提供商配置"""
        self.configurations[name] = config
        
    # 获取已保存配置的方法
    def get_configuration(self, name: str) -> Dict[str, Any]:
        """获取已保存的配置"""
        return self.configurations.get(name, {})

    # 添加提供商的方法
    def add_provider(self, name: str, config: Dict[str, Any]):
        """注册新的LLM服务提供商"""
        name_lower = name.lower()
        
        # 根据提供商名称创建相应的适配器实例
        if name_lower == 'ollama':
            self.providers[name] = OllamaAdapter(**config)
        elif name_lower == 'openai':
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
        elif name_lower == 'aliyun':
            self.providers[name] = AliyunAdapter(**config)
        elif name_lower == 'baidu':
            self.providers[name] = BaiduAdapter(**config)
        elif name_lower == 'deepseek':
            self.providers[name] = DeepSeekAdapter(**config)
        elif name_lower == 'moonshot':
            self.providers[name] = MoonshotAdapter(**config)
        elif name_lower == 'zhipu':
            self.providers[name] = ZhipuAdapter(**config)
        elif name_lower == 'spark':
            self.providers[name] = SparkAdapter(**config)
        elif name_lower == 'minimax':
            self.providers[name] = MinimaxAdapter(**config)
        elif name_lower == 'sensechat':
            self.providers[name] = SenseChatAdapter(**config)
        elif name_lower == 'xunfei':
            self.providers[name] = XunfeiAdapter(**config)
        elif name_lower == 'custom':
            self.providers[name] = CustomAdapter(**config)
        else:
            # 如果是不支持的提供商类型，则抛出 ValueError 异常
            raise ValueError(f"不支持的提供商类型: {name}")

    # 切换当前使用的 LLM 服务的方法
    def switch_current_provider(self, name: str):
        """切换当前使用的LLM服务"""
        # 检查提供商是否已注册
        if name not in self.providers:
            raise KeyError(f"未注册的提供商: {name}")
        self.current_provider = name  # 设置当前提供商
        logger.info(f"已切换到LLM服务提供商: {name}")  # 记录日志

    # 处理聊天请求并路由到当前提供商的方法
    async def handle_request(self, messages: list, model: str) -> str:
        """处理聊天请求并路由到当前提供商"""
        # 检查是否已选择 LLM 服务提供商
        if not self.current_provider:
            raise RuntimeError("未选择LLM服务提供商")
        
        # 获取当前提供商实例
        provider = self.providers.get(self.current_provider)
        if not provider:
            raise RuntimeError(f"无效的当前提供商: {self.current_provider}")

        try:
            # 调用当前提供商的 chat_completion 方法处理请求
            return await provider.chat_completion(messages, model)
        except Exception as e:
            # 捕获异常并记录错误日志
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
        logger.info("MCP配置已成功导入")  # 记录日志
