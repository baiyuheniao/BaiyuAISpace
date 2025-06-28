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
# 导入聊天历史记录管理模块
# from chat_history import ChatHistory  # 暂时注释掉，因为文件为空
# 导入Optional类型
from typing import Optional, List

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

# 创建聊天历史记录管理实例
# chat_history = ChatHistory()  # 暂时注释掉，因为文件为空

# 定义聊天请求的数据模型
class ChatRequest(BaseModel):
    messages: list  # 消息列表
    model: str = "default"  # 模型名称，默认为 "default"
    history_id: Optional[str] = None  # 聊天历史ID，可选

# 定义聊天历史记录的数据模型
class HistoryRequest(BaseModel):
    title: Optional[str] = None  # 历史记录标题，可选

# 定义聊天历史记录标题的数据模型
class HistoryTitleRequest(BaseModel):
    title: str  # 历史记录标题

# 定义聊天补全的 POST 接口
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    try:
        # 获取历史ID，如果没有则创建一个新的
        # history_id = request.history_id
        # if not history_id:
        #     history_id = chat_history.create_history()
        
        # 获取用户的最后一条消息
        user_message = request.messages[-1]
        
        # 将用户消息添加到历史记录
        # chat_history.add_message(history_id, user_message["role"], user_message["content"])
        
        # 调用 MCP 实例处理聊天请求
        response = await mcp.handle_request(request.messages, request.model)
        
        # 将 AI 助手的回复添加到历史记录
        # chat_history.add_message(history_id, "assistant", response)
        
        # 返回聊天补全结果
        return {
            "object": "chat.completion",
            # "history_id": history_id,
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

# 定义完整的MCP配置保存请求体模型
class MCPSaveConfigRequest(BaseModel):
    provider_name: str  # 提供商名称
    config: dict  # 配置字典
    mcp_config: dict  # MCP配置字典

# 定义切换提供商的请求体模型
class SwitchProviderRequest(BaseModel):
    provider_name: str  # 提供商名称
    config: dict  # 配置字典
    
# 定义切换提供商的 POST 接口
@app.post("/switch_provider")
async def switch_provider(request: SwitchProviderRequest):
    # 添加提供商
    mcp.add_provider(request.provider_name, request.config)
    # 切换当前提供商
    mcp.switch_current_provider(request.provider_name)
    return {"status": "success"}
    
# 定义保存 MCP 配置的 POST 接口
@app.post("/mcp/save_config")
async def save_mcp_config(request: MCPSaveConfigRequest):
    # 保存配置
    mcp.save_configuration(request.provider_name, request.config)
    # 如果有MCP配置，也保存到MCP模块中
    if request.mcp_config:
        mcp.import_configuration(request.mcp_config)
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

# 创建新的聊天历史记录
@app.post("/chat/histories")
async def create_chat_history(request: Optional[HistoryRequest] = None):
    # title = None
    # if request and request.title:
    #     title = request.title
    # history_id = chat_history.create_history(title)
    # return {"status": "success", "history_id": history_id}
    return {"status": "success", "message": "聊天历史功能暂未实现"}

# 获取所有聊天历史记录
@app.get("/chat/histories")
async def get_chat_histories():
    # histories = chat_history.get_histories()
    # return {"status": "success", "histories": histories}
    return {"status": "success", "histories": [], "message": "聊天历史功能暂未实现"}

# 获取收藏的聊天历史记录
@app.get("/chat/favorites")
async def get_favorite_histories():
    # favorites = chat_history.get_favorites()
    # return {"status": "success", "favorites": favorites}
    return {"status": "success", "favorites": [], "message": "聊天历史功能暂未实现"}

# 获取特定聊天历史记录
@app.get("/chat/histories/{history_id}")
async def get_chat_history(history_id: str):
    # history = chat_history.get_history(history_id)
    # if not history:
    #     raise HTTPException(status_code=404, detail="聊天历史记录不存在")
    # return {"status": "success", "history": history}
    raise HTTPException(status_code=404, detail="聊天历史功能暂未实现")

# 更新聊天历史记录标题
@app.put("/chat/histories/{history_id}/title")
async def update_chat_history_title(history_id: str, request: HistoryTitleRequest):
    # success = chat_history.update_history_title(history_id, request.title)
    # if not success:
    #     raise HTTPException(status_code=404, detail="聊天历史记录不存在")
    # return {"status": "success"}
    raise HTTPException(status_code=404, detail="聊天历史功能暂未实现")

# 切换聊天历史记录收藏状态
@app.put("/chat/histories/{history_id}/favorite")
async def toggle_chat_history_favorite(history_id: str):
    # success = chat_history.toggle_favorite(history_id)
    # if not success:
    #     raise HTTPException(status_code=404, detail="聊天历史记录不存在")
    # return {"status": "success"}
    raise HTTPException(status_code=404, detail="聊天历史功能暂未实现")

# 删除聊天历史记录
@app.delete("/chat/histories/{history_id}")
async def delete_chat_history(history_id: str):
    # success = chat_history.delete_history(history_id)
    # if not success:
    #     raise HTTPException(status_code=404, detail="聊天历史记录不存在")
    # return {"status": "success"}
    raise HTTPException(status_code=404, detail="聊天历史功能暂未实现")

# 清空所有聊天历史记录
@app.delete("/chat/histories")
async def clear_chat_histories():
    # chat_history.clear_all_histories()
    # return {"status": "success"}
    return {"status": "success", "message": "聊天历史功能暂未实现"}

# 当作为主程序运行时
if __name__ == "__main__":
    import uvicorn
    # 运行 FastAPI 应用，监听所有网络接口的 8000 端口
    uvicorn.run(app, host="0.0.0.0", port=8000)