#!/usr/bin/python
# coding:utf-8

"""
测试llmxapi的FortuneAgent
"""

import os
import sys

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.fortune_agent_llmx import FortuneAgentLLMX

def test_fortune_response():
    """测试占卜回复生成"""
    print("=" * 60)
    print("测试1: 占卜回复生成")
    print("=" * 60)
    
    # 创建Agent实例
    # 方式1: 直接传入API Key
    agent = FortuneAgentLLMX(
        api_key="sk-4ITgC1TTgVh4pgJHidHsEf30z6Y9u44q9FdtVUQhpEZRqI1Y",
        model="gemini-2.5-pro"  # 或其他模型如 "gpt-4o-mini"
    )
    
    # 方式2: 从环境变量读取（需要先设置 LLMX_API_KEY）
    # agent = FortuneAgentLLMX()
    
    # 测试不同的签级和运势类型
    test_cases = [
        {
            "username": "小明",
            "grade": "上上签",
            "topic": "love",
            "user_input": "我今天抽到上上签！"
        },
        {
            "username": "小红",
            "grade": "下签",
            "topic": "career",
            "user_input": "怎么又是下签啊..."
        },
        {
            "username": "小刚",
            "grade": "中签",
            "topic": "wealth",
            "user_input": None
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n【测试用例 {i}】")
        print(f"玩家: {case['username']}")
        print(f"签级: {case['grade']}")
        print(f"运势类型: {case['topic']}")
        print(f"玩家说: {case['user_input'] or '（无）'}")
        
        response = agent.make_fortune_response(
            username=case['username'],
            grade=case['grade'],
            topic=case['topic'],
            user_input=case['user_input']
        )
        
        print(f"占卜师回复: {response}")
        print("-" * 60)

def test_chat():
    """测试纯聊天模式"""
    print("\n" + "=" * 60)
    print("测试2: 纯聊天模式")
    print("=" * 60)
    
    agent = FortuneAgentLLMX(
        api_key="sk-4ITgC1TTgVh4pgJHidHsEf30z6Y9u44q9FdtVUQhpEZRqI1Y",
        model="gemini-2.5-pro"
    )
    
    # 测试不同的聊天场景
    chat_inputs = [
        "你好呀！",
        "你是AI吗？",
        "能教我编程吗？",
        "我想抽个签看看运势"
    ]
    
    for i, user_input in enumerate(chat_inputs, 1):
        print(f"\n【聊天测试 {i}】")
        print(f"观众说: {user_input}")
        
        response = agent.chat(user_input)
        
        print(f"占卜师回复: {response}")
        print("-" * 60)

def test_custom_rules():
    """测试自定义规则"""
    print("\n" + "=" * 60)
    print("测试3: 自定义规则")
    print("=" * 60)
    
    custom_rules = """
额外规则：
- 每次回复都要加上"阿弥陀佛"或"善哉善哉"
- 语气要更加佛系和禅意
"""
    
    agent = FortuneAgentLLMX(
        api_key="sk-4ITgC1TTgVh4pgJHidHsEf30z6Y9u44q9FdtVUQhpEZRqI1Y",
        model="gemini-2.5-pro",
        custom_rules=custom_rules
    )
    
    print(f"\n【自定义规则测试】")
    print(f"玩家: 小李")
    print(f"签级: 上签")
    print(f"运势类型: daily")
    
    response = agent.make_fortune_response(
        username="小李",
        grade="上签",
        topic="daily",
        user_input="今天运气怎么样？"
    )
    
    print(f"占卜师回复: {response}")
    print("-" * 60)

def test_different_models():
    """测试不同的模型"""
    print("\n" + "=" * 60)
    print("测试4: 不同模型对比")
    print("=" * 60)
    
    models = [
        "gemini-2.5-pro",
        "gpt-4o-mini",
        "claude-3-5-sonnet-20241022"
    ]
    
    for model in models:
        print(f"\n【测试模型: {model}】")
        try:
            agent = FortuneAgentLLMX(
                api_key="sk-4ITgC1TTgVh4pgJHidHsEf30z6Y9u44q9FdtVUQhpEZRqI1Y",
                model=model
            )
            
            response = agent.make_fortune_response(
                username="测试用户",
                grade="上上签",
                topic="love",
                user_input="太好了！"
            )
            
            print(f"回复: {response}")
        except Exception as e:
            print(f"错误: {e}")
        print("-" * 60)

if __name__ == "__main__":
    print("\n🎴 llmxapi FortuneAgent 测试脚本 🎴\n")
    
    try:
        # 运行所有测试
        test_fortune_response()
        test_chat()
        test_custom_rules()
        
        # 可选：测试不同模型（需要确保API支持这些模型）
        # test_different_models()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()