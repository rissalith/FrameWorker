#!/usr/bin/python
# coding:utf-8

"""
直接测试Gemini API连接
"""

import google.generativeai as genai
import sys

def test_gemini_api():
    """测试Gemini API"""
    api_key = 'sk-4ITgC1TTgVh4pgJHidHsEf30z6Y9u44q9FdtVUQhpEZRqI1Y'
    
    print("=" * 50)
    print("测试Gemini API连接")
    print("=" * 50)
    print(f"API Key: {api_key[:20]}...")
    print("=" * 50)
    
    try:
        # 配置API
        genai.configure(api_key=api_key)
        print("[1/3] API配置成功")
        
        # 创建模型
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        print("[2/3] 模型创建成功")
        
        # 发送测试请求
        print("[3/3] 发送测试请求...")
        prompt = "请用一句话回复：你好"
        
        response = model.generate_content(prompt)
        print(f"\n成功！AI回复: {response.text}")
        print("\n✓ Gemini API工作正常！")
        return True
        
    except Exception as e:
        print(f"\n✗ Gemini API调用失败:")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_gemini_api()
    sys.exit(0 if success else 1)