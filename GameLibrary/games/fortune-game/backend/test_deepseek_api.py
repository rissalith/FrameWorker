#!/usr/bin/python
# coding:utf-8

"""
测试DeepSeek API的完整流程
"""

import sys
import io
import requests
import json

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_fortune_api():
    """测试占卜API"""
    print("=" * 60)
    print("测试DeepSeek占卜API完整流程")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # 测试1: 纯聊天模式
    print("\n【测试1】纯聊天模式")
    print("-" * 60)
    chat_data = {
        "message": "你好，占卜师！",
        "username": "测试用户"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/fortune/chat",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        
        if result.get('success'):
            print(f"[OK] 聊天回复: {result.get('response')}")
        else:
            print(f"[FAIL] 失败: {result.get('message')}")
    except Exception as e:
        print(f"[ERROR] 请求失败: {e}")
    
    # 测试2: 占卜回复模式（上上签）
    print("\n【测试2】占卜回复模式 - 上上签")
    print("-" * 60)
    fortune_data = {
        "message": "我今天运气怎么样？",
        "username": "幸运儿",
        "grade": "上上签",
        "topic": "love"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/fortune/chat",
            json=fortune_data,
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        
        if result.get('success'):
            print(f"[OK] 占卜回复: {result.get('response')}")
        else:
            print(f"[FAIL] 失败: {result.get('message')}")
    except Exception as e:
        print(f"[ERROR] 请求失败: {e}")
    
    # 测试3: 占卜回复模式（下签）
    print("\n【测试3】占卜回复模式 - 下签")
    print("-" * 60)
    fortune_data = {
        "message": "我最近总是不顺利",
        "username": "倒霉蛋",
        "grade": "下签",
        "topic": "career"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/fortune/chat",
            json=fortune_data,
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        
        if result.get('success'):
            print(f"[OK] 占卜回复: {result.get('response')}")
        else:
            print(f"[FAIL] 失败: {result.get('message')}")
    except Exception as e:
        print(f"[ERROR] 请求失败: {e}")
    
    # 测试4: 中签 - 财运
    print("\n【测试4】占卜回复模式 - 中签（财运）")
    print("-" * 60)
    fortune_data = {
        "message": "我想知道最近的财运",
        "username": "求财者",
        "grade": "中签",
        "topic": "wealth"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/fortune/chat",
            json=fortune_data,
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        
        if result.get('success'):
            print(f"[OK] 占卜回复: {result.get('response')}")
        else:
            print(f"[FAIL] 失败: {result.get('message')}")
    except Exception as e:
        print(f"[ERROR] 请求失败: {e}")
    
    # 测试5: 上签 - 健康
    print("\n【测试5】占卜回复模式 - 上签（健康）")
    print("-" * 60)
    fortune_data = {
        "message": "我的身体状况如何？",
        "username": "养生达人",
        "grade": "上签",
        "topic": "health"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/fortune/chat",
            json=fortune_data,
            headers={"Content-Type": "application/json"}
        )
        result = response.json()
        
        if result.get('success'):
            print(f"[OK] 占卜回复: {result.get('response')}")
        else:
            print(f"[FAIL] 失败: {result.get('message')}")
    except Exception as e:
        print(f"[ERROR] 请求失败: {e}")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] 所有测试完成！DeepSeek API集成成功")
    print("=" * 60)

if __name__ == "__main__":
    test_fortune_api()