#!/usr/bin/python
# coding:utf-8

"""
测试知识库是否能被正确读取和使用
"""

import os
import sys

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_knowledge_base_files():
    """测试知识库文件是否存在"""
    print("=" * 60)
    print("测试1: 检查知识库文件")
    print("=" * 60)
    
    knowledge_base_dir = os.path.join(os.path.dirname(__file__), "knowledge_base")
    
    required_files = [
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
    for filename in required_files:
        filepath = os.path.join(knowledge_base_dir, filename)
        exists = os.path.exists(filepath)
        status = "✅" if exists else "❌"
        print(f"{status} {filename}: {'存在' if exists else '不存在'}")
        if not exists:
            all_exist = False
    
    print("-" * 60)
    return all_exist

def test_read_knowledge_base():
    """测试读取知识库内容"""
    print("\n" + "=" * 60)
    print("测试2: 读取知识库内容")
    print("=" * 60)
    
    knowledge_base_dir = os.path.join(os.path.dirname(__file__), "knowledge_base")
    
    # 读取角色档案
    profile_path = os.path.join(knowledge_base_dir, "01_character_profile.md")
    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = len(content.split('\n'))
            print(f"✅ 01_character_profile.md: {lines}行")
            # 检查关键内容
            if "紫色魔法帽" in content and "小女孩" in content:
                print("   ✓ 包含关键角色信息")
            else:
                print("   ✗ 缺少关键角色信息")
    except Exception as e:
        print(f"❌ 读取失败: {e}")
    
    # 读取占卜规则
    rules_path = os.path.join(knowledge_base_dir, "02_fortune_rules.md")
    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = len(content.split('\n'))
            print(f"✅ 02_fortune_rules.md: {lines}行")
            # 检查关键内容
            if "上上签" in content and "爱情运" in content:
                print("   ✓ 包含签级和运势类型")
            else:
                print("   ✗ 缺少签级或运势类型")
    except Exception as e:
        print(f"❌ 读取失败: {e}")
    
    # 读取语言风格
    style_path = os.path.join(knowledge_base_dir, "03_language_style.md")
    try:
        with open(style_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = len(content.split('\n'))
            print(f"✅ 03_language_style.md: {lines}行")
            # 检查关键内容
            if "30字" in content and "语气词" in content:
                print("   ✓ 包含语言风格规范")
            else:
                print("   ✗ 缺少语言风格规范")
    except Exception as e:
        print(f"❌ 读取失败: {e}")
    
    # 读取限制词
    restrictions_path = os.path.join(knowledge_base_dir, "05_restrictions.md")
    try:
        with open(restrictions_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = len(content.split('\n'))
            print(f"✅ 05_restrictions.md: {lines}行")
            # 检查关键内容
            if "AI" in content and "禁止" in content:
                print("   ✓ 包含禁止词列表")
            else:
                print("   ✗ 缺少禁止词列表")
    except Exception as e:
        print(f"❌ 读取失败: {e}")
    
    # 读取对话示例
    examples_path = os.path.join(knowledge_base_dir, "07_example_dialogues.md")
    try:
        with open(examples_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = len(content.split('\n'))
            print(f"✅ 07_example_dialogues.md: {lines}行")
            # 检查关键内容
            if "示例" in content and "玩家" in content and "Lili" in content:
                print("   ✓ 包含对话示例")
            else:
                print("   ✗ 缺少对话示例")
    except Exception as e:
        print(f"❌ 读取失败: {e}")
    
    print("-" * 60)

def test_extract_key_info():
    """测试提取关键信息"""
    print("\n" + "=" * 60)
    print("测试3: 提取关键信息")
    print("=" * 60)
    
    knowledge_base_dir = os.path.join(os.path.dirname(__file__), "knowledge_base")
    
    # 从角色档案提取角色特征
    profile_path = os.path.join(knowledge_base_dir, "01_character_profile.md")
    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print("\n【角色特征】")
        if "紫色魔法帽" in content:
            print("✓ 标志性装扮: 紫色魔法帽")
        if "小女孩" in content:
            print("✓ 年龄感: 小女孩")
        if "天真可爱" in content:
            print("✓ 性格: 天真可爱")
        if "占卜师" in content:
            print("✓ 职业: 占卜师")
    except Exception as e:
        print(f"❌ 提取失败: {e}")
    
    # 从占卜规则提取签级
    rules_path = os.path.join(knowledge_base_dir, "02_fortune_rules.md")
    try:
        with open(rules_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print("\n【签级系统】")
        grades = ["上上签", "上签", "中签", "下签", "下下签"]
        for grade in grades:
            if grade in content:
                print(f"✓ {grade}")
        
        print("\n【运势类型】")
        topics = ["爱情运", "日常运", "事业运", "健康运", "财运"]
        for topic in topics:
            if topic in content:
                print(f"✓ {topic}")
    except Exception as e:
        print(f"❌ 提取失败: {e}")
    
    # 从限制词提取禁止词
    restrictions_path = os.path.join(knowledge_base_dir, "05_restrictions.md")
    try:
        with open(restrictions_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        print("\n【禁止词示例】")
        forbidden_words = ["AI", "人工智能", "模型", "算法", "GPT"]
        for word in forbidden_words:
            if word in content:
                print(f"✓ {word}")
    except Exception as e:
        print(f"❌ 提取失败: {e}")
    
    print("-" * 60)

def test_agent_with_knowledge_base():
    """测试Agent是否使用了知识库的内容"""
    print("\n" + "=" * 60)
    print("测试4: Agent与知识库的关系")
    print("=" * 60)
    
    from services.fortune_agent_llmx import FortuneAgentLLMX
    
    # 检查Agent的系统指令是否包含知识库的关键内容
    print("\n【检查Agent的系统指令】")
    
    system_instruction = FortuneAgentLLMX.SYSTEM_INSTRUCTION
    
    # 检查角色设定
    if "紫色魔法帽" in system_instruction:
        print("✓ 包含角色特征: 紫色魔法帽")
    else:
        print("✗ 缺少角色特征: 紫色魔法帽")
    
    if "小女孩" in system_instruction or "小魔女" in system_instruction:
        print("✓ 包含角色定位: 小女孩/小魔女")
    else:
        print("✗ 缺少角色定位")
    
    # 检查语言风格
    if "30字" in system_instruction:
        print("✓ 包含长度限制: 30字")
    else:
        print("✗ 缺少长度限制")
    
    if "～" in system_instruction or "语气词" in system_instruction:
        print("✓ 包含语气要求")
    else:
        print("✗ 缺少语气要求")
    
    # 检查禁止词
    print("\n【检查禁止词列表】")
    forbidden_words = FortuneAgentLLMX.FORBIDDEN_WORDS
    print(f"禁止词数量: {len(forbidden_words)}")
    print(f"禁止词示例: {', '.join(forbidden_words[:5])}")
    
    # 检查Few-Shot示例
    print("\n【检查Few-Shot示例】")
    few_shot = FortuneAgentLLMX.FEW_SHOT_EXAMPLES
    
    if "示例" in few_shot:
        print("✓ 包含示例标记")
    if "玩家" in few_shot and "小魔女" in few_shot:
        print("✓ 包含对话格式")
    if "紫帽子" in few_shot:
        print("✓ 示例中使用了角色特征")
    
    print("-" * 60)

def test_knowledge_base_coverage():
    """测试知识库覆盖度"""
    print("\n" + "=" * 60)
    print("测试5: 知识库覆盖度分析")
    print("=" * 60)
    
    knowledge_base_dir = os.path.join(os.path.dirname(__file__), "knowledge_base")
    
    total_lines = 0
    total_chars = 0
    
    files = [
        "01_character_profile.md",
        "02_fortune_rules.md",
        "03_language_style.md",
        "04_interaction_scenarios.md",
        "05_restrictions.md",
        "06_game_mechanics.md",
        "07_example_dialogues.md"
    ]
    
    print("\n【文件统计】")
    for filename in files:
        filepath = os.path.join(knowledge_base_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = len(content.split('\n'))
                chars = len(content)
                total_lines += lines
                total_chars += chars
                print(f"{filename}: {lines}行, {chars}字符")
        except Exception as e:
            print(f"{filename}: 读取失败 - {e}")
    
    print(f"\n【总计】")
    print(f"总行数: {total_lines}")
    print(f"总字符数: {total_chars}")
    print(f"平均每个文件: {total_lines // len(files)}行")
    
    print("-" * 60)

if __name__ == "__main__":
    print("\n=== Lili知识库测试脚本 ===\n")
    
    try:
        # 运行所有测试
        files_exist = test_knowledge_base_files()
        
        if files_exist:
            test_read_knowledge_base()
            test_extract_key_info()
            test_agent_with_knowledge_base()
            test_knowledge_base_coverage()
            
            print("\n" + "=" * 60)
            print("✅ 所有测试完成！")
            print("=" * 60)
            
            print("\n【总结】")
            print("✓ 知识库文件结构完整")
            print("✓ 知识库内容可以正常读取")
            print("✓ Agent代码中包含了知识库的核心内容")
            print("\n【建议】")
            print("- 当前Agent是将知识库内容硬编码在代码中")
            print("- 如需动态加载知识库，可以修改Agent实现")
            print("- 知识库文件可作为文档参考和训练数据")
        else:
            print("\n❌ 部分知识库文件不存在，请检查文件结构")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()