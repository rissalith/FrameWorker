#!/usr/bin/python
# coding:utf-8

"""
测试占卜Agent API
"""

import requests
import json

def test_fortune_chat():
    """测试占卜聊天API"""
    url = 'http://localhost:5000/api/fortune/chat'
    
    payload = {
        'message': '你好',
        'api_key': 'sk-4ITgC1TTgVh4pgJHidHsEf30z6Y9u44q9FdtVUQhpEZRqI1Y'
    }
    
    print("=" * 50)
    print("测试占卜Agent API")
    print("=" * 50)
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    print("=" * 50)
    print("发送请求...")
    
    try:
        response = requests.post(
            url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=60  # 60秒超时
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ API调用成功！")
        else:
            print("\n❌ API调用失败！")
            
    except requests.exceptions.Timeout:
        print("\n❌ 请求超时（60秒）")
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务器，请确保后端服务器正在运行")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_fortune_chat()