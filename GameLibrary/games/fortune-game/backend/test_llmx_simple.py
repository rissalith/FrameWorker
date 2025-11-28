#!/usr/bin/python
# coding:utf-8

"""
简化的llmxapi测试脚本 - 用于诊断连接问题
"""

import os
import sys
from openai import OpenAI

def test_basic_connection():
    """测试基本连接"""
    print("=" * 60)
    print("测试 llmxapi 基本连接")
    print("=" * 60)
    
    api_key = "sk-4ITgC1TTgVh4pgJHidHsEf30z6Y9u44q9FdtVUQhpEZRqI1Y"
    base_url = "https://llmxapi.com/v1"
    model = "gemini-2.5-pro"
    
    print(f"\n配置信息:")
    print(f"  Base URL: {base_url}")
    print(f"  Model: {model}")
    print(f"  API Key: {api_key[:20]}...")
    
    try:
        print("\n正在创建客户端...")
        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=30.0  # 30秒超时
        )
        print("✓ 客户端创建成功")
        
        print("\n正在发送测试请求...")
        print("（这可能需要几秒钟，请耐心等待...）")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "你好，请用一句话介绍你自己"}
            ],
            max_tokens=50
        )
        
        print("\n✓ 请求成功！")
        print(f"\n回复内容: {response.choices[0].message.content}")
        print("\n" + "=" * 60)
        print("✅ 连接测试通过！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        print("\n可能的原因:")
        print("  1. 网络连接问题")
        print("  2. API Key 无效")
        print("  3. 需要配置代理")
        print("  4. 防火墙阻止连接")
        print("\n建议:")
        print("  - 检查网络连接")
        print("  - 确认 API Key 是否正确")
        print("  - 如果在国内，可能需要配置代理")
        return False

if __name__ == "__main__":
    print("\n🔍 llmxapi 连接诊断工具 🔍\n")
    test_basic_connection()