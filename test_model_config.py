#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型配置诊断脚本
用于检查当前配置的模型名称是否正确
"""

import asyncio
import json
from mcp_module import MCP

async def test_model_config():
    """测试当前模型配置"""
    print("=== 模型配置诊断工具 ===")
    
    # 创建MCP实例
    mcp = MCP()
    
    # 检查是否有配置
    if not mcp.configurations:
        print("❌ 没有找到任何配置")
        print("请先在设置页面配置API提供商和模型")
        return
    
    print(f"📋 找到 {len(mcp.configurations)} 个配置:")
    
    for provider_name, config in mcp.configurations.items():
        print(f"\n🔧 提供商: {provider_name}")
        print(f"   模型名称: {config.get('model', '未设置')}")
        print(f"   API密钥: {config.get('api_key', '未设置')[:10]}..." if config.get('api_key') else "   API密钥: 未设置")
        print(f"   Base URL: {config.get('base_url', '未设置')}")
        
        # 检查模型名称是否有效
        model_name = config.get('model')
        if not model_name or not str(model_name).strip():
            print("   ❌ 模型名称无效或为空")
        else:
            print(f"   ✅ 模型名称: {model_name}")
        
        # 检查是否是当前提供商
        if mcp.current_provider == provider_name:
            print("   🎯 当前活跃提供商")
            
            # 尝试创建提供商实例
            try:
                mcp.add_provider(provider_name, config)
                print("   ✅ 提供商实例创建成功")
                
                # 测试简单的聊天请求
                test_messages = [{"role": "user", "content": "你好"}]
                print(f"   🧪 测试聊天请求...")
                
                try:
                    result = await mcp.handle_request(test_messages, "test")
                    print(f"   ✅ 聊天请求成功，响应长度: {len(result)}")
                    print(f"   📝 响应内容: {result[:100]}...")
                except Exception as e:
                    print(f"   ❌ 聊天请求失败: {str(e)}")
                    
            except Exception as e:
                print(f"   ❌ 提供商实例创建失败: {str(e)}")
        else:
            print("   ⏸️  非当前提供商")
    
    print("\n=== 诊断完成 ===")
    print("\n💡 建议:")
    print("1. 确保模型名称正确且不为空")
    print("2. 检查API密钥是否有效")
    print("3. 确认Base URL是否正确")
    print("4. 验证模型名称在API服务商中是否存在")

if __name__ == "__main__":
    asyncio.run(test_model_config()) 