#!/usr/bin/python
# coding:utf-8

"""
测试紫帽子小魔女占卜师的角色形象
"""

import sys
import io
import requests
import json

# 设置标准输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test_miko_character():
    """测试小魔女角色"""
    print("=" * 60)
    print("测试紫帽子小魔女占卜师角色")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    test_cases = [
        {
            "name": "测试1: 问候",
            "data": {
                "message": "你好呀！",
                "username": "新观众"
            }
        },
        {
            "name": "测试2: 询问身份",
            "data": {
                "message": "你是谁呀？",
                "username": "好奇宝宝"
            }
        },
        {
            "name": "测试3: 上上签爱情",
            "data": {
                "message": "我想知道爱情运势",
                "username": "恋爱中",
                "grade": "上上签",
                "topic": "love"
            }
        },
        {
            "name": "测试4: 下下签事业",
            "data": {
                "message": "工作好难啊",
                "username": "打工人",
                "grade": "下下签",
                "topic": "career"
            }
        },
        {
            "name": "测试5: 中签日常",
            "data": {
                "message": "今天运气如何？",
                "username": "普通人",
                "grade": "中签",
                "topic": "daily"
            }
        },
        {
            "name": "测试6: 无关话题",
            "data": {
                "message": "今天天气真好",
                "username": "路人甲"
            }
        }
    ]
    
    for test in test_cases:
        print(f"\n{test['name']}")
        print("-" * 60)
        print(f"用户: {test['data']['username']} 说: {test['data']['message']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/fortune/chat",
                json=test['data'],
                headers={"Content-Type": "application/json"}
            )
            result = response.json()
            
            if result.get('success'):
                reply = result.get('response')
                print(f"小魔女: {reply}")
                print(f"字数: {len(reply)} 字")
            else:
                print(f"[FAIL] {result.get('message')}")
        except Exception as e:
            print(f"[ERROR] {e}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_miko_character()