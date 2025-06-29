#!/usr/bin/env python3
"""
测试后端API接口的脚本
"""
import asyncio
import aiohttp
import json

async def test_switch_provider():
    """测试切换提供商接口"""
    url = "http://localhost:8000/switch_provider"
    data = {
        "provider_name": "OpenAI",
        "config": {
            "api_key": "test_key",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7
        }
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data) as response:
                print(f"切换提供商响应状态: {response.status}")
                response_text = await response.text()
                print(f"响应内容: {response_text}")
                return response.status == 200
        except Exception as e:
            print(f"请求失败: {e}")
            return False

async def test_mcp_save_config():
    """测试MCP配置保存接口"""
    url = "http://localhost:8000/mcp/save_config"
    data = {
        "provider_name": "OpenAI",
        "config": {
            "api_key": "test_key",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7
        },
        "mcp_config": {
            "OpenAI": {
                "api_key": "test_key",
                "model": "gpt-3.5-turbo"
            }
        }
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data) as response:
                print(f"MCP保存配置响应状态: {response.status}")
                response_text = await response.text()
                print(f"响应内容: {response_text}")
                return response.status == 200
        except Exception as e:
            print(f"请求失败: {e}")
            return False

async def main():
    """主测试函数"""
    print("开始测试后端API接口...")
    
    print("\n1. 测试切换提供商接口:")
    success1 = await test_switch_provider()
    
    print("\n2. 测试MCP配置保存接口:")
    success2 = await test_mcp_save_config()
    
    print(f"\n测试结果:")
    print(f"切换提供商: {'成功' if success1 else '失败'}")
    print(f"MCP配置保存: {'成功' if success2 else '失败'}")

if __name__ == "__main__":
    asyncio.run(main()) 