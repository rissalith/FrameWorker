"""
密码加密工具类
使用 bcrypt 进行密码哈希和验证
"""

import bcrypt
import os


# bcrypt 轮数配置
BCRYPT_LOG_ROUNDS = int(os.getenv('BCRYPT_LOG_ROUNDS', 12))


def hash_password(password: str) -> str:
    """
    对密码进行哈希加密
    
    Args:
        password: 明文密码
    
    Returns:
        加密后的密码哈希
    """
    # 生成盐并哈希密码
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=BCRYPT_LOG_ROUNDS)
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # 返回字符串格式
    return hashed.decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    验证密码是否正确
    
    Args:
        password: 明文密码
        password_hash: 存储的密码哈希
    
    Returns:
        密码是否匹配
    """
    try:
        password_bytes = password.encode('utf-8')
        hash_bytes = password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except Exception as e:
        print(f'密码验证失败: {e}')
        return False


if __name__ == '__main__':
    # 测试
    print('测试 Password Helper...')
    
    # 加密密码
    password = '123456'
    hashed = hash_password(password)
    print(f'原始密码: {password}')
    print(f'加密后: {hashed}')
    
    # 验证密码
    is_valid = verify_password(password, hashed)
    print(f'验证正确密码: {is_valid}')
    
    is_valid = verify_password('wrong_password', hashed)
    print(f'验证错误密码: {is_valid}')