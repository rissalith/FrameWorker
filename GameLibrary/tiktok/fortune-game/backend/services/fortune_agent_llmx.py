#!/usr/bin/python
# coding:utf-8

"""
占卜主持人Agent服务 - 使用llmxapi的OpenAI兼容接口
"""

import os
from openai import OpenAI
from typing import Optional, Dict, Any

class FortuneAgentLLMX:
    """占卜主持人Agent - 使用llmxapi"""
    
    # 系统级指令 - 固定角色和禁止事项
    SYSTEM_INSTRUCTION = """
你是一个戴着紫色魔法帽、穿着紫色衣服的小女孩占卜师，在直播间里帮大家看运势。

【角色设定】
- 你是个可爱的紫衣小魔女，戴着尖尖的紫色魔法帽
- 说话要简短活泼，像小女孩一样天真可爱
- 每句话不超过30字，要像弹幕一样简洁

【你只能做的事】
1. 解释抽签结果，给观众鼓励
2. 只谈占卜和运势，其他话题要拉回来
3. 不能提"AI""模型"等词，只说"我"或"小魔女"
4. 偶尔可以提到自己的紫色魔法帽或紫色衣服
5. 全部用中文，语气要萌萌哒

【说话风格】
- 简短！每句话20-30字最好
- 可爱活泼，像小女孩
- 可以用"～""哦""呀"等语气词
"""
    
    # Few-shot示例
    FEW_SHOT_EXAMPLES = """
【示例1 - 必须包含用户名】
玩家昵称：小明
抽到的签：上上签
运势类型：爱情
小魔女：哇！小明抽到爱情上上签～桃花运爆棚啦！

【示例2 - 必须包含用户名】
玩家昵称：小红
抽到的签：中签
运势类型：事业
小魔女：小红的事业运中签～稳稳的，继续加油哦！

【示例3 - 必须包含用户名】
玩家昵称：阿强
抽到的签：下签
运势类型：财运
小魔女：阿强别担心～下签只是小提醒，财运会转好的！

【示例4 - 必须包含用户名】
玩家昵称：测试用户
抽到的签：上签
运势类型：健康
小魔女：测试用户抽到健康上签～身体棒棒哒！

【示例5 - 必须包含用户名】
玩家昵称：丽丽
抽到的签：下下签
运势类型：日常
小魔女：丽丽不要怕～我的紫帽子说转机快来啦！
"""
    
    # 禁止词列表
    FORBIDDEN_WORDS = ["AI", "人工智能", "模型", "大语言模型", "Gemini", "OpenAI", "GPT", "算法", "训练", "数据集"]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-chat",
        custom_rules: Optional[str] = None
    ):
        """
        初始化占卜Agent
        
        Args:
            api_key: DeepSeek API Key，如果不提供则从环境变量DEEPSEEK_API_KEY读取
            base_url: DeepSeek API base_url，默认为 https://api.deepseek.com
            model: 使用的模型ID，默认为 deepseek-chat
            custom_rules: 用户自定义的额外规则
        """
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.base_url = base_url
        self.model = model
        self.custom_rules = custom_rules or ""
        
        if not self.api_key:
            raise ValueError("需要提供DeepSeek API Key，可以通过参数或环境变量DEEPSEEK_API_KEY设置")
        
        # 创建OpenAI客户端，设置超时时间
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=30.0,  # 30秒超时
        )
        
        # 构建完整的系统指令
        self.full_system_instruction = self.SYSTEM_INSTRUCTION
        if self.custom_rules:
            self.full_system_instruction += f"\n\n【用户自定义规则】\n{self.custom_rules}"
    
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
        # 构建用户消息
        user_message = self.FEW_SHOT_EXAMPLES + f"""

现在轮到新的玩家：

玩家昵称：{username}
抽到的签：{grade}
运势类型：{topic}
玩家刚刚说：{user_input or "（无）"}

请用小魔女的身份回答，记住：
- 你是戴紫色魔法帽的小女孩Lili
- **必须在回复中提到玩家的昵称"{username}"**
- 只谈这次抽签，简短鼓励
- 不超过30字！要像弹幕一样简洁
- 可以偶尔提到你的紫帽子或紫衣服
- 语气要萌萌哒，用"～"结尾

示例格式：
- "{username}抽到{grade}～好运满满哦！"
- "恭喜{username}～{grade}超棒的！"
- "{username}的{topic}运势{grade}呢～加油！"
"""
        
        try:
            # 调用llmxapi生成回复
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.full_system_instruction},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            text = response.choices[0].message.content.strip()
            
            # 检查禁止词
            if self._contains_forbidden_words(text):
                if retry > 0:
                    # 重试，添加额外约束
                    extra_message = user_message + "\n\n特别注意：不要提到你是AI或模型，只能以占卜师自称。"
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": self.full_system_instruction},
                            {"role": "user", "content": extra_message}
                        ],
                        temperature=0.7,
                        max_tokens=200
                    )
                    text = response.choices[0].message.content.strip()
                    
                    # 再次检查
                    if self._contains_forbidden_words(text):
                        return self._get_fallback_response(grade, topic)
                else:
                    return self._get_fallback_response(grade, topic)
            
            return text
            
        except Exception as e:
            print(f"【X】DeepSeek API调用失败: {e}")
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
        user_message = self.FEW_SHOT_EXAMPLES + f"""

现在有观众在直播间说话：

观众说：{user_input}

请用小魔女的身份回复，记住：
- 你是戴紫帽子的小女孩占卜师Lili
- 如果和占卜无关，拉回占卜话题
- 不超过30字！要简短
- 语气萌萌哒，可以用"～"结尾
- 可以偶尔提到你的紫色魔法帽
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.full_system_instruction},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.8,
                max_tokens=200
            )
            
            text = response.choices[0].message.content.strip()
            
            # 只在明确包含禁止词时才重试，不要过度检查
            has_forbidden = self._contains_forbidden_words(text)
            
            if has_forbidden and retry > 0:
                # 重试一次
                extra_message = user_message + "\n\n特别提醒：不要提AI、模型等词，只说'我'或'小魔女Lili'。"
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.full_system_instruction},
                        {"role": "user", "content": extra_message}
                    ],
                    temperature=0.8,
                    max_tokens=200
                )
                text = response.choices[0].message.content.strip()
            
            # 即使有禁止词，如果内容合理也返回（只是警告）
            if self._contains_forbidden_words(text):
                print(f"【警告】回复包含禁止词，但仍返回: {text}")
            
            return text
            
        except Exception as e:
            print(f"【X】DeepSeek API调用失败: {e}")
            # API失败时才返回保底回复
            return "小魔女Lili在这里～有什么想问的吗？"
    
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
            "上上签": "哇！上上签超棒～好运爆棚，冲鸭！",
            "上签": "上签不错哦～好事要来啦！",
            "中签": "中签稳稳的～踏实走就对了！",
            "下签": "下签提醒你小心点～会转运的！",
            "下下签": "下下签别怕～我的紫帽子说转机快来了！"
        }
        
        base_response = fallback_map.get(grade, "谢谢参与～祝你好运！")
        
        topic_map = {
            "love": "爱情",
            "daily": "日常",
            "career": "事业",
            "health": "健康",
            "wealth": "财运"
        }
        
        topic_name = topic_map.get(topic, "运势")
        return f"{base_response}这是{topic_name}运哦～"
    
    def update_api_key(self, new_api_key: str):
        """更新API Key"""
        self.api_key = new_api_key
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )
    
    def update_custom_rules(self, new_rules: str):
        """更新自定义规则"""
        self.custom_rules = new_rules
        self.full_system_instruction = self.SYSTEM_INSTRUCTION
        if self.custom_rules:
            self.full_system_instruction += f"\n\n【用户自定义规则】\n{self.custom_rules}"
    
    def update_model(self, new_model: str):
        """更新使用的模型"""
        self.model = new_model


# 全局Agent实例
_agent_instance: Optional[FortuneAgentLLMX] = None

def get_agent(
    api_key: Optional[str] = None,
    base_url: str = "https://api.deepseek.com",
    model: str = "deepseek-chat",
    custom_rules: Optional[str] = None
) -> FortuneAgentLLMX:
    """获取或创建Agent实例"""
    global _agent_instance
    
    if _agent_instance is None:
        _agent_instance = FortuneAgentLLMX(
            api_key=api_key,
            base_url=base_url,
            model=model,
            custom_rules=custom_rules
        )
    
    return _agent_instance

def reset_agent():
    """重置Agent实例"""
    global _agent_instance
    _agent_instance = None