# Multi-LLM Management Platform / 多模态LLM管理平台

## 项目概述 | Overview
统一管理多个LLM服务提供商的中间件，支持动态配置和切换不同AI服务商。采用前后端分离架构，前端基于Vue3+ElementPlus，后端使用Python异步框架。

## 核心功能 | Features
✅ 多服务商接入（OpenAI/Anthropic/阿里云/智谱等）  
✅ 运行时动态切换服务商  
✅ 标准化API接口  
✅ 服务商配置集中管理
支持MCP功能

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