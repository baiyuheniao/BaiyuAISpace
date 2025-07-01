#!/usr/bin/env python3
"""
测试聊天功能的脚本
"""
import asyncio
import aiohttp
import json

async def test_chat_completion():
    """测试聊天补全接口"""
    url = "http://localhost:8000/v1/chat/completions"
    data = {
        "messages": [
            {"role": "user", "content": "你好，请介绍一下你自己"}
        ],
        "model": "default"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data) as response:
                print(f"聊天请求响应状态: {response.status}")
                response_text = await response.text()
                print(f"响应内容: {response_text}")
                
                if response.status == 200:
                    result = json.loads(response_text)
                    if 'choices' in result and result['choices']:
                        content = result['choices'][0]['message']['content']
                        print(f"AI回复: {content}")
                        return True
                    else:
                        print("响应格式不正确")
                        return False
                else:
                    print(f"请求失败: {response_text}")
                    return False
        except Exception as e:
            print(f"请求异常: {e}")
            return False

async def test_mcp_status():
    """测试MCP状态"""
    url = "http://localhost:8000/mcp/get_configs"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                print(f"MCP状态响应: {response.status}")
                response_text = await response.text()
                print(f"MCP配置: {response_text}")
                return response.status == 200
        except Exception as e:
            print(f"MCP状态检查失败: {e}")
            return False

async def main():
    """主测试函数"""
    print("开始测试聊天功能...")
    
    print("\n1. 检查MCP状态:")
    mcp_ok = await test_mcp_status()
    
    print("\n2. 测试聊天功能:")
    chat_ok = await test_chat_completion()
    
    print(f"\n测试结果:")
    print(f"MCP状态: {'正常' if mcp_ok else '异常'}")
    print(f"聊天功能: {'正常' if chat_ok else '异常'}")
    
    if not mcp_ok:
        print("\n建议: 请先在设置页面配置AI服务提供商")
    elif not chat_ok:
        print("\n建议: 请检查AI服务提供商的配置是否正确")

if __name__ == "__main__":
    asyncio.run(main()) 