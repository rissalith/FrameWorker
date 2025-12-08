#!/usr/bin/python
# coding:utf-8

"""
测试DeepSeek API调用
"""

import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.fortune_agent_llmx import FortuneAgentLLMX

def test_deepseek_api():
    """测试DeepSeek API"""
    print("=" * 50)
    print("测试DeepSeek API调用")
    print("=" * 50)
    
    # 使用提供的API密钥
    api_key = "sk-6e43a71eb7be48aab365ac4de2623e86"
    
    try:
        # 创建Agent实例
        print("\n1. 创建Agent实例...")
        agent = FortuneAgentLLMX(
            api_key=api_key,
            base_url="https://api.deepseek.com",
            model="deepseek-chat"
        )
        print("✓ Agent创建成功")
        
        # 测试占卜回复
        print("\n2. 测试占卜回复...")
        response = agent.make_fortune_response(
            username="测试用户",
            grade="上上签",
            topic="love",
            user_input="我今天运气怎么样？"
        )
        print(f"✓ 占卜回复: {response}")
        
        # 测试聊天功能
        print("\n3. 测试聊天功能...")
        chat_response = agent.chat("你好，占卜师！")
        print(f"✓ 聊天回复: {chat_response}")
        
        print("\n" + "=" * 50)
        print("✓ 所有测试通过！DeepSeek API工作正常")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_deepseek_api()