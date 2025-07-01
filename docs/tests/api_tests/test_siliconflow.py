#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
硅基流动API测试脚本
用于测试API连接、获取模型列表和验证模型名称
"""

import asyncio
import aiohttp
import json
import sys

class SiliconFlowTester:
    def __init__(self, api_key: str, base_url: str = "https://api.siliconflow.cn"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def test_connection(self):
        """测试API连接"""
        print(f"🔗 测试连接到: {self.base_url}")
        try:
            async with aiohttp.ClientSession() as session:
                # 尝试获取模型列表
                # 智能构建models URL，避免重复添加/v1
                if self.base_url.endswith('/v1'):
                    models_url = f"{self.base_url}/models"
                else:
                    models_url = f"{self.base_url}/v1/models"
                print(f"📋 获取模型列表: {models_url}")
                
                async with session.get(models_url, headers=self.headers) as response:
                    if response.status == 200:
                        models_data = await response.json()
                        print("✅ API连接成功!")
                        print(f"📊 响应状态: {response.status}")
                        return models_data
                    else:
                        error_text = await response.text()
                        print(f"❌ API连接失败: {response.status}")
                        print(f"错误详情: {error_text}")
                        return None
        except Exception as e:
            print(f"❌ 连接异常: {str(e)}")
            return None
    
    async def get_models(self):
        """获取可用模型列表"""
        models_data = await self.test_connection()
        if models_data and 'data' in models_data:
            models = models_data['data']
            print(f"\n📋 可用模型列表 ({len(models)} 个):")
            for i, model in enumerate(models, 1):
                model_id = model.get('id', '未知')
                model_name = model.get('object', '未知')
                print(f"  {i}. {model_id} ({model_name})")
            return [model.get('id') for model in models]
        else:
            print("❌ 无法获取模型列表")
            return []
    
    async def test_chat_completion(self, model: str, test_message: str = "你好"):
        """测试聊天补全"""
        print(f"\n💬 测试聊天补全 - 模型: {model}")
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": test_message}
            ],
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # 智能构建chat URL，避免重复添加/v1
                if self.base_url.endswith('/v1'):
                    chat_url = f"{self.base_url}/chat/completions"
                else:
                    chat_url = f"{self.base_url}/v1/chat/completions"
                print(f"🌐 请求URL: {chat_url}")
                print(f"📤 请求数据: {json.dumps(payload, ensure_ascii=False, indent=2)}")
                
                async with session.post(
                    chat_url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(60)
                ) as response:
                    response_text = await response.text()
                    print(f"📥 响应状态: {response.status}")
                    
                    if response.status == 200:
                        result = json.loads(response_text)
                        print("✅ 聊天补全成功!")
                        print(f"🤖 回复: {result['choices'][0]['message']['content']}")
                        return True
                    else:
                        print(f"❌ 聊天补全失败: {response.status}")
                        print(f"错误详情: {response_text}")
                        
                        # 尝试解析错误信息
                        try:
                            error_data = json.loads(response_text)
                            if 'message' in error_data:
                                print(f"错误消息: {error_data['message']}")
                        except:
                            pass
                        return False
        except Exception as e:
            print(f"❌ 请求异常: {str(e)}")
            return False

async def main():
    print("🚀 硅基流动API测试工具")
    print("=" * 50)
    
    # 获取API密钥
    api_key = input("请输入您的API密钥: ").strip()
    if not api_key:
        print("❌ API密钥不能为空")
        return
    
    # 获取Base URL
    base_url = input("请输入Base URL (默认: https://api.siliconflow.cn): ").strip()
    if not base_url:
        base_url = "https://api.siliconflow.cn"
    
    # 创建测试器
    tester = SiliconFlowTester(api_key, base_url)
    
    # 测试连接和获取模型列表
    models = await tester.get_models()
    
    if models:
        print(f"\n🎯 找到 {len(models)} 个可用模型")
        
        # 让用户选择要测试的模型
        if len(models) == 1:
            test_model = models[0]
            print(f"自动选择唯一模型: {test_model}")
        else:
            print("\n请选择要测试的模型:")
            for i, model in enumerate(models, 1):
                print(f"  {i}. {model}")
            
            try:
                choice = int(input(f"请输入选择 (1-{len(models)}): ")) - 1
                if 0 <= choice < len(models):
                    test_model = models[choice]
                else:
                    print("❌ 无效选择")
                    return
            except ValueError:
                print("❌ 请输入有效数字")
                return
        
        # 测试聊天补全
        await tester.test_chat_completion(test_model)
    else:
        print("❌ 无法获取模型列表，请检查API密钥和网络连接")

if __name__ == "__main__":
    asyncio.run(main()) 