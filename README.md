# Multi-LLM Management Platform / 多模态LLM管理平台

## 项目概述 | Overview
统一管理多个LLM服务提供商的中间件，支持动态配置和切换不同AI服务商。采用前后端分离架构，前端基于Vue3+ElementPlus，后端使用Python异步框架。

## 核心功能 | Features
✅ 多服务商接入（OpenAI/Anthropic/阿里云/智谱等）  
✅ 运行时动态切换服务商  
✅ 标准化API接口  
✅ 服务商配置集中管理
✅ 支持MCP功能

## 技术栈 | Tech Stack
**前端**  
`Vue3` `ElementPlus` `Axios` `Vue-Router`

**后端**  
`Python 3.10+` `FastAPI` `AsyncIO` `Pydantic`

## 快速启动 | Installation
```bash
# 后端服务
pip install -r requirements.txt
uvicorn server:app --reload

# 前端服务
cd frontend
pnpm install
pnpm run serve
```

## 配置说明

### 前端配置

- **当前提供商**: 选择当前使用的API服务提供商。
- **API密钥**: 输入您所选提供商的API密钥。
- **模型名称**: 输入您希望调用的模型名称。
- **Temperature**: 控制模型输出的随机性，值越大越随机。
- **Top K**: 从Top K个最高概率的词中进行采样。
- **Max Tokens**: 限制模型生成响应的最大token数量。
- **MCP模式**: 用于切换是否启用多路并发处理（Multi-Concurrent Processing）模式。
- **MCP配置**: 在MCP模式下，用户可以在此输入JSON格式的配置，用于定义不同服务提供商的详细参数。例如：`{ &quot;provider_name&quot;: { &quot;api_key&quot;: &quot;your_api_key&quot;, &quot;model_name&quot;: &quot;your_model_name&quot; } }`。请注意，JSON字符串中的双引号需要转义为`&quot;`。

### 后端配置

后端配置主要通过 `server.py` 和 `mcp_module.py` 进行管理。您可以通过修改 `mcp_module.py` 中的适配器配置来支持更多LLM服务。