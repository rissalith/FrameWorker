"""
输入验证工具类
验证手机号、验证码等输入格式
"""

import re
from typing import Tuple


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    验证手机号格式
    
    Args:
        phone: 手机号字符串
    
    Returns:
        (是否有效, 错误信息)
    """
    if not phone:
        return False, '手机号不能为空'
    
    # 移除空格和特殊字符
    phone = phone.strip().replace(' ', '').replace('-', '')
    
    # 中国大陆手机号正则：1开头，第二位是3-9，共11位
    pattern = r'^1[3-9]\d{9}$'
    
    if not re.match(pattern, phone):
        return False, '手机号格式不正确'
    
    return True, ''


def validate_code(code: str) -> Tuple[bool, str]:
    """
    验证验证码格式
    
    Args:
        code: 验证码字符串
    
    Returns:
        (是否有效, 错误信息)
    """
    if not code:
        return False, '验证码不能为空'
    
    code = code.strip()
    
    # 验证码应该是6位数字
    if not code.isdigit():
        return False, '验证码只能包含数字'
    
    if len(code) != 6:
        return False, '验证码必须是6位数字'
    
    return True, ''


def validate_nickname(nickname: str) -> Tuple[bool, str]:
    """
    验证昵称格式
    
    Args:
        nickname: 昵称字符串
    
    Returns:
        (是否有效, 错误信息)
    """
    if not nickname:
        return False, '昵称不能为空'
    
    nickname = nickname.strip()
    
    # 昵称长度限制：2-20个字符
    if len(nickname) < 2:
        return False, '昵称至少2个字符'
    
    if len(nickname) > 20:
        return False, '昵称最多20个字符'
    
    # 不允许特殊字符（只允许中文、英文、数字、下划线）
    pattern = r'^[\u4e00-\u9fa5a-zA-Z0-9_]+$'
    if not re.match(pattern, nickname):
        return False, '昵称只能包含中文、英文、数字和下划线'
    
    return True, ''


def validate_password(password: str) -> Tuple[bool, str]:
    """
    验证密码格式
    
    Args:
        password: 密码字符串
    
    Returns:
        (是否有效, 错误信息)
    """
    if not password:
        return False, '密码不能为空'
    
    # 密码长度限制：6-20个字符
    if len(password) < 6:
        return False, '密码至少6个字符'
    
    if len(password) > 20:
        return False, '密码最多20个字符'
    
    return True, ''


if __name__ == '__main__':
    # 测试
    print('测试 Validators...')
    
    # 测试手机号验证
    test_phones = [
        '13800138000',  # 有效
        '12345678901',  # 无效（第二位不是3-9）
        '138001380',    # 无效（长度不够）
        '',             # 无效（空）
    ]
    
    print('\n手机号验证:')
    for phone in test_phones:
        is_valid, msg = validate_phone(phone)
        print(f'  {phone}: {"✓" if is_valid else "✗"} {msg}')
    
    # 测试验证码验证
    test_codes = [
        '123456',   # 有效
        '12345',    # 无效（长度不够）
        'abc123',   # 无效（包含字母）
        '',         # 无效（空）
    ]
    
    print('\n验证码验证:')
    for code in test_codes:
        is_valid, msg = validate_code(code)
        print(f'  {code}: {"✓" if is_valid else "✗"} {msg}')
    
    # 测试昵称验证
    test_nicknames = [
        '张三',         # 有效
        'User123',      # 有效
        '用户_001',     # 有效
        'A',            # 无效（太短）
        '这是一个非常非常非常长的昵称',  # 无效（太长）
        'User@123',     # 无效（包含特殊字符）
    ]
    
    print('\n昵称验证:')
    for nickname in test_nicknames:
        is_valid, msg = validate_nickname(nickname)
        print(f'  {nickname}: {"✓" if is_valid else "✗"} {msg}')