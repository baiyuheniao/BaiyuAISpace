# 从 fastapi 库导入 FastAPI 和 HTTPException
from fastapi import FastAPI, HTTPException
# 从 fastapi.middleware.cors 导入 CORSMiddleware，用于处理跨域请求
from fastapi.middleware.cors import CORSMiddleware
# 从 pydantic 库导入 BaseModel，用于数据模型定义
from pydantic import BaseModel
# 从 mcp_module 导入 MCP 类
from mcp_module import MCP
# 导入 api_adapter 模块
import api_adapter

# 创建 FastAPI 应用实例
app = FastAPI()

# 允许跨域请求 (CORS) 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,  # 允许发送凭据
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 创建 MCP 实例，用于管理 LLM 服务提供商
mcp = MCP()

# 定义聊天请求的数据模型
class ChatRequest(BaseModel):
    messages: list  # 消息列表
    model: str = "default"  # 模型名称，默认为 "default"

# 定义聊天补全的 POST 接口
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    try:
        # 调用 MCP 实例处理聊天请求
        response = await mcp.handle_request(request.messages, request.model)
        # 返回聊天补全结果
        return {
            "object": "chat.completion",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": response
                }
            }]
        }
    except Exception as e:
        # 捕获异常并返回 HTTP 500 错误
        raise HTTPException(status_code=500, detail=str(e))

# 定义 MCP 配置的数据模型
class MCPConfig(BaseModel):
    provider_name: str  # 提供商名称
    config: dict  # 配置字典
    
# 定义切换提供商的 POST 接口
@app.post("/switch_provider")
async def switch_provider(provider_name: str, config: dict):
    # 添加提供商
    mcp.add_provider(provider_name, config)
    # 切换当前提供商
    mcp.switch_current_provider(provider_name)
    return {"status": "success"}
    
# 定义保存 MCP 配置的 POST 接口
@app.post("/mcp/save_config")
async def save_mcp_config(config: MCPConfig):
    # 保存配置
    mcp.save_configuration(config.provider_name, config.config)
    return {"status": "success"}
    
# 定义获取 MCP 配置的 GET 接口
@app.get("/mcp/get_configs")
async def get_mcp_configs():
    # 返回所有配置
    return {"configurations": mcp.configurations}

# 定义导出 MCP 配置的 GET 接口
@app.get("/mcp/export_config")
async def export_mcp_config():
    # 导出配置
    return mcp.export_configuration()

# 定义导入 MCP 配置的 POST 接口
@app.post("/mcp/import_config")
async def import_mcp_config(config: dict):
    # 导入配置
    mcp.import_configuration(config)
    return {"status": "success"}

# 当作为主程序运行时
if __name__ == "__main__":
    import uvicorn
    # 运行 FastAPI 应用，监听所有网络接口的 8000 端口
    uvicorn.run(app, host="0.0.0.0", port=8000)