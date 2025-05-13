from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mcp_module import MCP
import api_adapter

app = FastAPI()

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mcp = MCP()

class ChatRequest(BaseModel):
    messages: list
    model: str = "default"

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatRequest):
    try:
        response = await mcp.handle_request(request.messages, request.model)
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
        raise HTTPException(status_code=500, detail=str(e))

class MCPConfig(BaseModel):
    provider_name: str
    config: dict
    
@app.post("/switch_provider")
async def switch_provider(provider_name: str, config: dict):
    mcp.add_provider(provider_name, config)
    mcp.switch_current_provider(provider_name)
    return {"status": "success"}
    
@app.post("/mcp/save_config")
async def save_mcp_config(config: MCPConfig):
    mcp.save_configuration(config.provider_name, config.config)
    return {"status": "success"}
    
@app.get("/mcp/get_configs")
async def get_mcp_configs():
    return {"configurations": mcp.configurations}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)