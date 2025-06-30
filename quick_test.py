#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试硅基流动聊天模型
"""

import asyncio
import aiohttp
import json

async def quick_test():
    # 你的配置
    api_key = "sk-pfuheaclxikegudowrqzurklagjdnphmydhrzzfeedbaicjc"
    base_url = "https://api.siliconflow.cn/v1"
    
    # 测试的聊天模型
    test_models = [
        "Qwen/Qwen2.5-7B-Instruct",
        "Qwen/Qwen2.5-14B-Instruct", 
        "Qwen/Qwen2.5-32B-Instruct",
        "deepseek-ai/DeepSeek-V2.5",
        "deepseek-ai/DeepSeek-V3"
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("🚀 快速测试硅基流动聊天模型")
    print("=" * 50)
    
    for model in test_models:
        print(f"\n🧪 测试模型: {model}")
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": "你好，请简单介绍一下你自己"}
            ],
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                chat_url = f"{base_url}/chat/completions"
                
                async with session.post(
                    chat_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result['choices'][0]['message']['content']
                        print(f"✅ 成功! 回复: {content[:100]}...")
                        print(f"🎉 模型 {model} 可以正常使用!")
                        return model  # 返回第一个成功的模型
                    else:
                        error_text = await response.text()
                        print(f"❌ 失败: {response.status} - {error_text}")
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
    
    print("\n❌ 所有测试模型都失败了")
    return None

if __name__ == "__main__":
    result = asyncio.run(quick_test())
    if result:
        print(f"\n🎯 推荐使用的模型: {result}")
        print("请在设置页面使用这个模型名称") 