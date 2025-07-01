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



# 从 fastapi 库导入 FastAPI 和 HTTPException
from fastapi import FastAPI, HTTPException, File, UploadFile
# 从 fastapi.middleware.cors 导入 CORSMiddleware，用于处理跨域请求
from fastapi.middleware.cors import CORSMiddleware
# 从 pydantic 库导入 BaseModel，用于数据模型定义
from pydantic import BaseModel
# 从 mcp_module 导入 MCP 类
from mcp_module import MCP
# 导入 api_adapter 模块
import api_adapter
# 导入聊天历史记录管理模块
from chat_history import ChatHistory  # 取消注释，已实现
# 导入Optional类型
from typing import Optional, List
import datetime
import os
import json
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

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
chat_history = ChatHistory()  # 取消注释，已实现

# 定义聊天请求的数据模型
class ChatRequest(BaseModel):
    messages: list  # 消息列表
    model: str = "default"  # 模型名称，默认为 "default"
    history_id: Optional[str] = None  # 聊天历史ID，可选
    file_urls: Optional[list] = None  # 新增，图片/视频URL列表

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
        print(f"收到聊天请求: 消息数={len(request.messages)}, 模型={request.model}, 文件数={len(request.file_urls) if request.file_urls else 0}")
        
        # 检查MCP实例是否有当前提供商
        if not mcp.current_provider:
            raise HTTPException(status_code=500, detail="未配置AI服务提供商，请先在设置页面配置")
        
        # 检查提供商是否存在
        if mcp.current_provider not in mcp.providers:
            raise HTTPException(status_code=500, detail=f"当前提供商 {mcp.current_provider} 不存在")
        
        # 聊天历史ID处理
        history_id = request.history_id
        if history_id:
            # 只保存最后一条用户消息，避免重复
            if request.messages and isinstance(request.messages, list):
                last_user_msg = None
                # 倒序找最后一条role为user的消息
                for msg in reversed(request.messages):
                    if isinstance(msg, dict) and msg.get('role') == 'user':
                        last_user_msg = msg
                        break
                if last_user_msg:
                    chat_history.add_message(history_id, last_user_msg)
        
        # 调用 MCP 实例处理聊天请求，传递 file_urls
        file_urls = request.file_urls if isinstance(request.file_urls, list) else None
        response = await mcp.handle_request(request.messages, request.model, file_urls=file_urls)
        print(f"聊天请求处理成功，响应长度: {len(response)}")
        
        # 保存AI回复到历史
        if history_id:
            ai_msg = {"role": "assistant", "content": response}
            chat_history.add_message(history_id, ai_msg)
        
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
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        print(f"聊天请求处理失败: {str(e)}")
        # 捕获异常并返回 HTTP 500 错误
        raise HTTPException(status_code=500, detail=f"聊天请求处理失败: {str(e)}")

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
    try:
        print(f"切换提供商: 提供商={request.provider_name}, 配置={request.config}")
        
        # 先保存配置到本地存储
        mcp.save_configuration(request.provider_name, request.config)
        print(f"配置已保存到本地存储: {request.provider_name}")
        
        # 检查提供商是否已经存在，如果不存在则添加
        if request.provider_name not in mcp.providers:
            print(f"提供商 {request.provider_name} 不存在，正在添加...")
            try:
                mcp.add_provider(request.provider_name, request.config)
                print(f"提供商 {request.provider_name} 添加成功")
            except Exception as add_error:
                print(f"添加提供商失败: {str(add_error)}")
                raise HTTPException(status_code=500, detail=f"添加提供商失败: {str(add_error)}")
        
        # 切换当前提供商
        try:
            mcp.switch_current_provider(request.provider_name)
            print(f"提供商切换成功: {request.provider_name}")
        except Exception as switch_error:
            print(f"切换提供商失败: {str(switch_error)}")
            raise HTTPException(status_code=500, detail=f"切换提供商失败: {str(switch_error)}")
        
        return {"status": "success", "message": f"提供商 {request.provider_name} 配置成功"}
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        print(f"切换提供商失败: {str(e)}")
        # 捕获异常并返回详细的错误信息
        raise HTTPException(status_code=500, detail=f"切换提供商失败: {str(e)}")
    
# 定义保存 MCP 配置的 POST 接口
@app.post("/mcp/save_config")
async def save_mcp_config(request: MCPSaveConfigRequest):
    try:
        print(f"保存MCP配置: 提供商={request.provider_name}, 配置={request.config}")
        # 保存配置
        mcp.save_configuration(request.provider_name, request.config)
        # 添加提供商到MCP实例中
        mcp.add_provider(request.provider_name, request.config)
        # 切换当前提供商
        mcp.switch_current_provider(request.provider_name)
        # 如果有MCP配置，也保存到MCP模块中
        if request.mcp_config:
            mcp.import_configuration(request.mcp_config)
        print(f"MCP配置保存成功: {request.provider_name}")
        return {"status": "success"}
    except Exception as e:
        print(f"MCP配置保存失败: {str(e)}")
        # 捕获异常并返回详细的错误信息
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")
    
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
    title = None
    if request and request.title:
        title = request.title
    history_id = chat_history.create_history(title)
    return {"status": "success", "history_id": history_id}

# 获取所有聊天历史记录
@app.get("/chat/histories")
async def get_chat_histories():
    histories = chat_history.get_histories()
    return {"status": "success", "histories": histories}

# 获取收藏的聊天历史记录
@app.get("/chat/favorites")
async def get_favorite_histories():
    favorites = chat_history.get_favorites()
    return {"status": "success", "favorites": favorites}

# 获取指定聊天历史记录
@app.get("/chat/histories/{history_id}")
async def get_chat_history(history_id: str):
    history = chat_history.get_history(history_id)
    if not history:
        raise HTTPException(status_code=404, detail="聊天历史记录不存在")
    return {"status": "success", "history": history}

# 更新聊天历史记录标题
@app.put("/chat/histories/{history_id}/title")
async def update_chat_history_title(history_id: str, request: HistoryTitleRequest):
    success = chat_history.update_history_title(history_id, request.title)
    if not success:
        raise HTTPException(status_code=404, detail="聊天历史记录不存在")
    return {"status": "success"}

# 切换聊天历史记录收藏状态
@app.put("/chat/histories/{history_id}/favorite")
async def toggle_chat_history_favorite(history_id: str):
    success = chat_history.toggle_favorite(history_id)
    if not success:
        raise HTTPException(status_code=404, detail="聊天历史记录不存在")
    return {"status": "success"}

# 删除聊天历史记录
@app.delete("/chat/histories/{history_id}")
async def delete_chat_history(history_id: str):
    success = chat_history.delete_history(history_id)
    if not success:
        raise HTTPException(status_code=404, detail="聊天历史记录不存在")
    return {"status": "success"}

# 清空所有聊天历史记录
@app.delete("/chat/histories")
async def clear_chat_histories():
    chat_history.clear_all_histories()
    return {"status": "success"}

# 定义获取当前配置的 GET 接口
@app.get("/current_config")
async def get_current_config():
    """获取当前配置信息"""
    try:
        if not mcp.current_provider:
            return {
                "status": "no_config",
                "message": "未配置任何提供商"
            }
        
        current_config = mcp.configurations.get(mcp.current_provider, {})
        return {
            "status": "success",
            "provider_name": mcp.current_provider,
            "config": current_config
        }
    except Exception as e:
        print(f"获取当前配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")

# 定义获取所有已保存配置的 GET 接口
@app.get("/saved_configs")
async def get_saved_configs():
    """获取所有已保存的配置"""
    try:
        return {
            "status": "success",
            "configurations": mcp.configurations,
            "current_provider": mcp.current_provider
        }
    except Exception as e:
        print(f"获取已保存配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")

# 定义删除配置的 DELETE 接口
@app.delete("/config/{provider_name}")
async def delete_config(provider_name: str):
    """删除指定提供商的配置"""
    try:
        if provider_name in mcp.configurations:
            del mcp.configurations[provider_name]
            # 如果删除的是当前提供商，清空当前提供商
            if mcp.current_provider == provider_name:
                mcp.current_provider = None
            mcp.save_configurations()
            return {"status": "success", "message": f"配置 {provider_name} 已删除"}
        else:
            raise HTTPException(status_code=404, detail=f"配置 {provider_name} 不存在")
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除配置失败: {str(e)}")

# 定义设置配置文件路径的请求体模型
class ConfigPathRequest(BaseModel):
    config_path: str  # 配置文件路径

# 定义设置配置文件路径的 POST 接口
@app.post("/set_config_path")
async def set_config_path(request: ConfigPathRequest):
    """设置配置文件路径"""
    try:
        # 验证路径格式
        if not request.config_path.strip():
            raise HTTPException(status_code=400, detail="配置文件路径不能为空")
        
        # 设置新的配置文件路径
        mcp.set_config_file(request.config_path)
        
        return {
            "status": "success",
            "message": f"配置文件路径已设置为: {request.config_path}",
            "config_path": request.config_path
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"设置配置文件路径失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"设置配置文件路径失败: {str(e)}")

# 定义获取配置文件路径的 GET 接口
@app.get("/get_config_path")
async def get_config_path():
    """获取当前配置文件路径"""
    try:
        return {
            "status": "success",
            "config_path": mcp.config_file
        }
    except Exception as e:
        print(f"获取配置文件路径失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取配置文件路径失败: {str(e)}")

# 定义备份配置的 GET 接口
@app.get("/backup_config")
async def backup_config():
    """备份当前配置"""
    try:
        # 获取当前配置
        backup_data = {
            "configurations": mcp.configurations,
            "current_provider": mcp.current_provider,
            "config_file": mcp.config_file,
            "backup_time": str(datetime.datetime.now()),
            "version": "1.0"
        }
        
        # 生成备份文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"mcp_config_backup_{timestamp}.json"
        
        # 保存备份文件
        backup_path = os.path.join(os.path.dirname(mcp.config_file), backup_filename)
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        return {
            "status": "success",
            "message": f"配置备份成功: {backup_filename}",
            "backup_file": backup_filename,
            "backup_path": backup_path
        }
    except Exception as e:
        print(f"备份配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"备份配置失败: {str(e)}")

# 定义恢复配置的 POST 接口
@app.post("/restore_config")
async def restore_config(backup_data: dict):
    """从备份恢复配置"""
    try:
        # 验证备份数据格式
        if "configurations" not in backup_data:
            raise HTTPException(status_code=400, detail="无效的备份文件格式")
        
        # 恢复配置
        mcp.configurations = backup_data.get("configurations", {})
        mcp.current_provider = backup_data.get("current_provider")
        
        # 保存配置
        mcp.save_configurations()
        
        return {
            "status": "success",
            "message": "配置恢复成功",
            "restored_providers": list(mcp.configurations.keys()),
            "current_provider": mcp.current_provider
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"恢复配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"恢复配置失败: {str(e)}")

# 定义调试信息的 GET 接口
@app.get("/debug_info")
async def get_debug_info():
    """获取调试信息"""
    try:
        debug_info = {
            "current_provider": mcp.current_provider,
            "saved_configurations": mcp.configurations,
            "available_providers": list(mcp.providers.keys()),
            "config_file_path": mcp.config_file,
            "config_file_exists": os.path.exists(mcp.config_file)
        }
        
        # 如果有当前提供商，添加详细信息
        if mcp.current_provider:
            current_config = mcp.configurations.get(mcp.current_provider, {})
            debug_info["current_provider_config"] = {
                "api_key": current_config.get('api_key', '')[:10] + "..." if current_config.get('api_key') else '未设置',
                "model": current_config.get('model', '未设置'),
                "base_url": current_config.get('base_url', '未设置'),
                "temperature": current_config.get('temperature', '未设置'),
                "max_tokens": current_config.get('max_tokens', '未设置'),
                "top_p": current_config.get('top_p', '未设置'),
                "top_k": current_config.get('top_k', '未设置')
            }
        
        return {
            "status": "success",
            "debug_info": debug_info
        }
    except Exception as e:
        print(f"获取调试信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取调试信息失败: {str(e)}")

# 定义配置编辑的请求体模型
class EditConfigRequest(BaseModel):
    provider_name: str  # 提供商名称
    config: dict  # 配置字典

# 定义配置编辑的 PUT 接口
@app.put("/config/{provider_name}")
async def edit_config(provider_name: str, request: EditConfigRequest):
    try:
        print(f"编辑配置: 提供商={provider_name}, 配置={request.config}")
        
        # 验证提供商名称是否匹配
        if provider_name != request.provider_name:
            raise HTTPException(status_code=400, detail="提供商名称不匹配")
        
        # 保存更新后的配置
        mcp.save_configuration(provider_name, request.config)
        print(f"配置更新成功: {provider_name}")
        
        return {"status": "success", "message": f"配置 {provider_name} 更新成功"}
    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        print(f"编辑配置失败: {str(e)}")
        # 捕获异常并返回详细的错误信息
        raise HTTPException(status_code=500, detail=f"编辑配置失败: {str(e)}")

# 定义获取聊天页面配置的 GET 接口
@app.get("/chat/configs")
async def get_chat_configs():
    try:
        # 获取所有已保存的配置
        configurations = mcp.get_all_configurations()
        current_provider = mcp.current_provider
        
        return {
            "status": "success",
            "configs": configurations,
            "current_provider": current_provider
        }
    except Exception as e:
        print(f"获取聊天配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp4', '.mov', '.avi', '.webm'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

@app.post('/chat/upload')
async def upload_file(file: UploadFile = File(...)):
    filename = file.filename or ""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {ext}")
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件过大，最大支持50MB")
    save_path = os.path.join(UPLOAD_DIR, filename)
    # 防止重名覆盖
    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(save_path):
        save_path = os.path.join(UPLOAD_DIR, f"{base}_{counter}{ext}")
        counter += 1
    with open(save_path, 'wb') as f:
        f.write(contents)
    # 返回相对URL，前端可用/static/访问
    file_url = f"/static/uploads/{os.path.basename(save_path)}"
    return JSONResponse({"url": file_url, "filename": os.path.basename(save_path)})

# 静态文件路由，供前端访问上传的文件
app.mount("/static/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# 当作为主程序运行时
if __name__ == "__main__":
    import uvicorn
    # 运行 FastAPI 应用，监听所有网络接口的 8000 端口
    uvicorn.run(app, host="0.0.0.0", port=8000)