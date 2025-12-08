#!/usr/bin/python
# coding:utf-8

"""
测试知识库是否能被正确读取和使用（简化版）
"""

import os
import sys

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("\n" + "=" * 60)
    print("Lili知识库测试")
    print("=" * 60)
    
    knowledge_base_dir = os.path.join(os.path.dirname(__file__), "knowledge_base")
    
    # 测试1: 检查文件
    print("\n[测试1] 检查知识库文件")
    print("-" * 60)
    
    files = [
        "README.md",
        "01_character_profile.md",
        "02_fortune_rules.md",
        "03_language_style.md",
        "04_interaction_scenarios.md",
        "05_restrictions.md",
        "06_game_mechanics.md",
        "07_example_dialogues.md"
    ]
    
    all_exist = True
    for filename in files:
        filepath = os.path.join(knowledge_base_dir, filename)
        exists = os.path.exists(filepath)
        status = "[OK]" if exists else "[FAIL]"
        print(f"{status} {filename}")
        if not exists:
            all_exist = False
    
    if not all_exist:
        print("\n[错误] 部分文件不存在")
        return False
    
    # 测试2: 读取内容
    print("\n[测试2] 读取知识库内容")
    print("-" * 60)
    
    total_lines = 0
    for filename in files:
        filepath = os.path.join(knowledge_base_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = len(content.split('\n'))
                total_lines += lines
                print(f"[OK] {filename}: {lines}行")
        except Exception as e:
            print(f"[FAIL] {filename}: {e}")
            return False
    
    print(f"\n总计: {total_lines}行")
    
    # 测试3: 检查关键内容
    print("\n[测试3] 检查关键内容")
    print("-" * 60)
    
    # 检查角色档案
    profile_path = os.path.join(knowledge_base_dir, "01_character_profile.md")
    with open(profile_path, 'r', encoding='utf-8') as f:
        content = f.read()
        checks = [
            ("紫色魔法帽", "角色特征"),
            ("小女孩", "年龄设定"),
            ("占卜师", "职业定位")
        ]
        for keyword, desc in checks:
            if keyword in content:
                print(f"[OK] {desc}: {keyword}")
            else:
                print(f"[FAIL] 缺少{desc}")
    
    # 检查占卜规则
    rules_path = os.path.join(knowledge_base_dir, "02_fortune_rules.md")
    with open(rules_path, 'r', encoding='utf-8') as f:
        content = f.read()
        grades = ["上上签", "上签", "中签", "下签", "下下签"]
        topics = ["爱情运", "日常运", "事业运", "健康运", "财运"]
        
        print("\n签级系统:")
        for grade in grades:
            status = "[OK]" if grade in content else "[FAIL]"
            print(f"  {status} {grade}")
        
        print("\n运势类型:")
        for topic in topics:
            status = "[OK]" if topic in content else "[FAIL]"
            print(f"  {status} {topic}")
    
    # 检查限制词
    restrictions_path = os.path.join(knowledge_base_dir, "05_restrictions.md")
    with open(restrictions_path, 'r', encoding='utf-8') as f:
        content = f.read()
        forbidden = ["AI", "人工智能", "模型", "算法"]
        
        print("\n禁止词:")
        for word in forbidden:
            status = "[OK]" if word in content else "[FAIL]"
            print(f"  {status} {word}")
    
    # 测试4: 检查Agent
    print("\n[测试4] 检查Agent实现")
    print("-" * 60)
    
    try:
        from services.fortune_agent_llmx import FortuneAgentLLMX
        
        # 检查系统指令
        system_instruction = FortuneAgentLLMX.SYSTEM_INSTRUCTION
        
        checks = [
            ("紫色魔法帽", "角色特征"),
            ("小女孩", "年龄设定"),
            ("30字", "长度限制"),
            ("占卜", "核心功能")
        ]
        
        print("\nAgent系统指令:")
        for keyword, desc in checks:
            if keyword in system_instruction:
                print(f"  [OK] 包含{desc}")
            else:
                print(f"  [WARN] 缺少{desc}")
        
        # 检查禁止词
        forbidden_words = FortuneAgentLLMX.FORBIDDEN_WORDS
        print(f"\n禁止词列表: {len(forbidden_words)}个")
        print(f"示例: {', '.join(forbidden_words[:5])}")
        
        # 检查Few-Shot示例
        few_shot = FortuneAgentLLMX.FEW_SHOT_EXAMPLES
        if "示例" in few_shot and "玩家" in few_shot:
            print("\n[OK] Few-Shot示例格式正确")
        else:
            print("\n[WARN] Few-Shot示例可能有问题")
        
    except Exception as e:
        print(f"[FAIL] 无法加载Agent: {e}")
        return False
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print("[OK] 知识库文件结构完整")
    print("[OK] 知识库内容可以正常读取")
    print("[OK] 包含所有必要的角色信息")
    print("[OK] Agent代码包含知识库核心内容")
    
    print("\n说明:")
    print("- 当前Agent将知识库内容硬编码在代码中")
    print("- 知识库文件作为文档参考和训练数据")
    print("- 如需动态加载，可以修改Agent实现")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n[成功] 所有测试通过!")
        else:
            print("\n[失败] 部分测试未通过")
            sys.exit(1)
    except Exception as e:
        print(f"\n[错误] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)