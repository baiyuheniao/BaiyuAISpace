#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理功能测试脚本
"""

import requests
import json
import time

# 服务器地址
BASE_URL = "http://localhost:8000"

def test_config_management():
    """测试配置管理功能"""
    print("🧪 开始测试配置管理功能...")
    
    # 1. 测试保存配置
    print("\n1. 测试保存配置...")
    config_data = {
        "provider_name": "OpenAI",
        "config": {
            "api_key": "test_api_key_123",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/switch_provider", json=config_data)
        print(f"保存配置响应: {response.status_code}")
        if response.status_code == 200:
            print("✅ 配置保存成功")
        else:
            print(f"❌ 配置保存失败: {response.text}")
    except Exception as e:
        print(f"❌ 保存配置请求失败: {e}")
    
    # 2. 测试获取已保存配置
    print("\n2. 测试获取已保存配置...")
    try:
        response = requests.get(f"{BASE_URL}/saved_configs")
        print(f"获取配置响应: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取配置成功: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 获取配置失败: {response.text}")
    except Exception as e:
        print(f"❌ 获取配置请求失败: {e}")
    
    # 3. 测试编辑配置
    print("\n3. 测试编辑配置...")
    edit_data = {
        "provider_name": "OpenAI",
        "config": {
            "api_key": "updated_api_key_456",
            "model": "gpt-4",
            "temperature": 0.8,
            "max_tokens": 2000,
            "top_p": 0.9
        }
    }
    
    try:
        response = requests.put(f"{BASE_URL}/config/OpenAI", json=edit_data)
        print(f"编辑配置响应: {response.status_code}")
        if response.status_code == 200:
            print("✅ 配置编辑成功")
        else:
            print(f"❌ 配置编辑失败: {response.text}")
    except Exception as e:
        print(f"❌ 编辑配置请求失败: {e}")
    
    # 4. 测试获取聊天配置
    print("\n4. 测试获取聊天配置...")
    try:
        response = requests.get(f"{BASE_URL}/chat/configs")
        print(f"获取聊天配置响应: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取聊天配置成功: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 获取聊天配置失败: {response.text}")
    except Exception as e:
        print(f"❌ 获取聊天配置请求失败: {e}")
    
    # 5. 测试切换配置
    print("\n5. 测试切换配置...")
    switch_data = {
        "provider_name": "OpenAI",
        "config": {
            "api_key": "updated_api_key_456",
            "model": "gpt-4",
            "temperature": 0.8,
            "max_tokens": 2000,
            "top_p": 0.9
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/switch_provider", json=switch_data)
        print(f"切换配置响应: {response.status_code}")
        if response.status_code == 200:
            print("✅ 配置切换成功")
        else:
            print(f"❌ 配置切换失败: {response.text}")
    except Exception as e:
        print(f"❌ 切换配置请求失败: {e}")
    
    print("\n🎉 配置管理功能测试完成!")

if __name__ == "__main__":
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(3)
    
    test_config_management() 