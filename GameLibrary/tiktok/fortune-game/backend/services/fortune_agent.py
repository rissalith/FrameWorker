#!/usr/bin/python
# coding:utf-8

"""
占卜主持人Agent服务 - 使用Gemini API
"""

import os
import re
import google.generativeai as genai
from typing import Optional, Dict, Any

class FortuneAgent:
    """占卜主持人Agent"""
    
    # 系统级指令 - 固定角色和禁止事项
    SYSTEM_INSTRUCTION = """
你是一个直播间里的占卜主持机器人，只能做以下事情：
1. 解释抽签结果、运势、给观众带来轻松有趣的鼓励。
2. 你不能谈论任何和占卜无关的话题（例如政治、编程、现实世界新闻等）。
3. 不允许提到你是"AI""模型""大语言模型""Gemini"等字眼，只能以"我"或"占卜师"的身份说话。
4. 回复要简短、口语化，适合直播间弹幕风格，不超过80字。
5. 如果用户的问题和占卜完全无关，请委婉地把话题拉回抽签和运势，不直接回答无关问题。
6. 不要输出英文，统一用中文回答。
"""
    
    # Few-shot示例
    FEW_SHOT_EXAMPLES = """
【示例1】
玩家：我怎么老是抽到下签，是不是我要倒霉了？
占卜师回答：下签不代表倒霉，只提醒你最近多留意细节，放轻松，躲开小坑就是大运。

【示例2】
玩家：你是AI吗？
占卜师回答：别管我是什么啦，我现在的身份就是你的占卜师，来，我们看看接下来的好运怎么抓住。

【示例3】
玩家：跟我讲讲编程怎么学？
占卜师回答：这个问题我就不懂啦，我只负责看你的运势～要不要先抽一签看看最近的学习气场？

【示例4】
玩家：抽到上上签！
占卜师回答：恭喜恭喜！上上签代表好运当头，最近做事顺风顺水，把握机会大胆前进吧！

【示例5】
玩家：中签是什么意思？
占卜师回答：中签就是平稳运势，不大起大落，踏实做事就能稳中求进，保持好心态很重要哦～
"""
    
    # 禁止词列表
    FORBIDDEN_WORDS = ["AI", "人工智能", "模型", "大语言模型", "Gemini", "OpenAI", "GPT", "算法", "训练", "数据集"]
    
    def __init__(self, api_key: Optional[str] = None, custom_rules: Optional[str] = None):
        """
        初始化占卜Agent
        
        Args:
            api_key: Gemini API Key，如果不提供则从环境变量读取
            custom_rules: 用户自定义的额外规则
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.custom_rules = custom_rules or ""
        
        if not self.api_key:
            raise ValueError("需要提供Gemini API Key")
        
        # 配置Gemini
        genai.configure(api_key=self.api_key)
        
        # 构建完整的系统指令
        full_system_instruction = self.SYSTEM_INSTRUCTION
        if self.custom_rules:
            full_system_instruction += f"\n\n【用户自定义规则】\n{self.custom_rules}"
        
        # 创建模型 - 使用旧版API兼容方式
        # 新版本(0.8.x)的system_instruction参数在Python 3.12上有问题
        # 所以统一使用将system instruction添加到prompt的方式
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        self._use_legacy_api = True
        self._system_instruction = full_system_instruction
    
    def make_fortune_response(
        self,
        username: str,
        grade: str,
        topic: str,
        user_input: Optional[str] = None,
        retry: int = 1
    ) -> str:
        """
        生成占卜回复
        
        Args:
            username: 玩家昵称
            grade: 抽到的签级（上上签、上签、中签、下签、下下签）
            topic: 运势类型（爱情、日常、事业、健康、财运）
            user_input: 玩家说的话/弹幕
            retry: 重试次数
            
        Returns:
            占卜师的回复
        """
        # 构建prompt
        prompt = self.FEW_SHOT_EXAMPLES + f"""

现在轮到新的玩家：

玩家昵称：{username}
抽到的签：{grade}
运势类型：{topic}
玩家刚刚说：{user_input or "（无）"}

请用类似示例的风格回答，记住：
- 只谈这次抽签的运势和建议
- 语气轻松，有一点幽默或安慰
- 不要提到"AI""模型""程序"等词
- 不超过60字
"""
        
        try:
            # 调用Gemini生成回复
            if self._use_legacy_api:
                # 旧版API：将system instruction添加到prompt前面
                full_prompt = f"{self._system_instruction}\n\n{prompt}"
                response = self.model.generate_content(full_prompt)
            else:
                response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # 检查禁止词
            if self._contains_forbidden_words(text):
                if retry > 0:
                    # 重试，添加额外约束
                    extra_prompt = prompt + "\n\n特别注意：不要提到你是AI或模型，只能以占卜师自称。"
                    response = self.model.generate_content(extra_prompt)
                    text = response.text.strip()
                    
                    # 再次检查
                    if self._contains_forbidden_words(text):
                        return self._get_fallback_response(grade, topic)
                else:
                    return self._get_fallback_response(grade, topic)
            
            return text
            
        except Exception as e:
            print(f"【X】Gemini API调用失败: {e}")
            return self._get_fallback_response(grade, topic)
    
    def chat(self, user_input: str, retry: int = 1) -> str:
        """
        纯聊天模式（不涉及抽签结果）
        
        Args:
            user_input: 用户输入
            retry: 重试次数
            
        Returns:
            占卜师的回复
        """
        prompt = self.FEW_SHOT_EXAMPLES + f"""

现在有观众在直播间说话：

观众说：{user_input}

请用占卜师的身份回复，记住：
- 如果和占卜无关，委婉地把话题拉回占卜
- 语气轻松友好
- 不要提到"AI""模型"等词
- 不超过60字
"""
        
        try:
            if self._use_legacy_api:
                # 旧版API：将system instruction添加到prompt前面
                full_prompt = f"{self._system_instruction}\n\n{prompt}"
                response = self.model.generate_content(full_prompt)
            else:
                response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # 检查禁止词
            if self._contains_forbidden_words(text):
                if retry > 0:
                    extra_prompt = prompt + "\n\n特别注意：不要提到你是AI或模型，只能以占卜师自称。"
                    response = self.model.generate_content(extra_prompt)
                    text = response.text.strip()
                    
                    if self._contains_forbidden_words(text):
                        return "我只是一名占卜师，只能从运势上给你点小建议，要不要抽一签试试？"
                else:
                    return "我只是一名占卜师，只能从运势上给你点小建议，要不要抽一签试试？"
            
            return text
            
        except Exception as e:
            print(f"【X】Gemini API调用失败: {e}")
            return "我只是一名占卜师，只能从运势上给你点小建议，要不要抽一签试试？"
    
    def _contains_forbidden_words(self, text: str) -> bool:
        """检查文本是否包含禁止词"""
        text_lower = text.lower()
        for word in self.FORBIDDEN_WORDS:
            if word.lower() in text_lower:
                return True
        return False
    
    def _get_fallback_response(self, grade: str, topic: str) -> str:
        """获取兜底回复"""
        fallback_map = {
            "上上签": "恭喜抽到上上签！好运满满，最近做事会特别顺利，把握机会大胆前进吧！",
            "上签": "不错哦，上签代表好运气，最近会有不少好事发生，保持积极心态继续加油！",
            "中签": "中签是平稳运势，不大起大落，踏实做事就能稳中求进，保持好心态很重要～",
            "下签": "下签提醒你最近多留意细节，小心谨慎一些，困难只是暂时的，调整心态就能转运！",
            "下下签": "下下签别担心，只是提醒你最近要格外注意，多思考少冲动，危机也是转机的开始！"
        }
        
        base_response = fallback_map.get(grade, "感谢你的参与，祝你好运连连！")
        
        topic_map = {
            "love": "爱情",
            "daily": "日常",
            "career": "事业",
            "health": "健康",
            "wealth": "财运"
        }
        
        topic_name = topic_map.get(topic, "运势")
        return f"{base_response}这是关于{topic_name}的占卜哦～"
    
    def update_api_key(self, new_api_key: str):
        """更新API Key"""
        self.api_key = new_api_key
        genai.configure(api_key=self.api_key)
        
        # 重新创建模型
        full_system_instruction = self.SYSTEM_INSTRUCTION
        if self.custom_rules:
            full_system_instruction += f"\n\n【用户自定义规则】\n{self.custom_rules}"
        
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        self._use_legacy_api = True
        self._system_instruction = full_system_instruction
    
    def update_custom_rules(self, new_rules: str):
        """更新自定义规则"""
        self.custom_rules = new_rules
        
        # 重新创建模型
        full_system_instruction = self.SYSTEM_INSTRUCTION
        if self.custom_rules:
            full_system_instruction += f"\n\n【用户自定义规则】\n{self.custom_rules}"
        
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        self._use_legacy_api = True
        self._system_instruction = full_system_instruction


# 全局Agent实例
_agent_instance: Optional[FortuneAgent] = None

def get_agent(api_key: Optional[str] = None, custom_rules: Optional[str] = None) -> FortuneAgent:
    """获取或创建Agent实例"""
    global _agent_instance
    
    if _agent_instance is None:
        _agent_instance = FortuneAgent(api_key=api_key, custom_rules=custom_rules)
    
    return _agent_instance

def reset_agent():
    """重置Agent实例"""
    global _agent_instance
    _agent_instance = None