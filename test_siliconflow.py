#!/usr/bin/env python3
"""
测试硅基流动API的脚本
"""
import asyncio
import aiohttp
import json

async def test_siliconflow_direct():
    """直接测试硅基流动API"""
    # 请替换为你的实际API密钥和模型名称
    api_key = "your_api_key_here"  # 请替换为实际的API密钥
    model = "your_model_name_here"  # 请替换为实际的模型名称
    
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "messages": [
            {"role": "user", "content": "你好，请介绍一下你自己"}
        ],
        "stream": False
    }
    
    print(f"测试硅基流动API:")
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {data}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data, headers=headers) as response:
                print(f"响应状态: {response.status}")
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

async def test_custom_adapter():
    """测试CustomAdapter"""
    from api_adapter import CustomAdapter
    
    # 请替换为你的实际配置
    api_key = "your_api_key_here"  # 请替换为实际的API密钥
    base_url = "https://api.siliconflow.cn/v1"  # 硅基流动的base_url
    model = "your_model_name_here"  # 请替换为实际的模型名称
    
    print(f"测试CustomAdapter:")
    print(f"API Key: {api_key[:10]}..." if len(api_key) > 10 else f"API Key: {api_key}")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    
    try:
        adapter = CustomAdapter(api_key=api_key, base_url=base_url)
        messages = [{"role": "user", "content": "你好，请介绍一下你自己"}]
        
        result = await adapter.chat_completion(messages, model)
        print(f"CustomAdapter测试成功: {result}")
        return True
    except Exception as e:
        print(f"CustomAdapter测试失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("开始测试硅基流动API...")
    
    print("\n注意: 请先替换脚本中的API密钥和模型名称")
    print("1. 在test_siliconflow_direct()函数中替换api_key和model")
    print("2. 在test_custom_adapter()函数中替换api_key和model")
    
    # 取消注释下面的行来运行测试
    # print("\n1. 直接测试硅基流动API:")
    # success1 = await test_siliconflow_direct()
    
    # print("\n2. 测试CustomAdapter:")
    # success2 = await test_custom_adapter()
    
    # print(f"\n测试结果:")
    # print(f"直接API测试: {'成功' if success1 else '失败'}")
    # print(f"CustomAdapter测试: {'成功' if success2 else '失败'}")

if __name__ == "__main__":
    asyncio.run(main()) 