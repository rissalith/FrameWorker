"""
JWT Token 工具类
用于生成和验证 JWT 令牌
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt


# JWT 配置
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 604800))  # 7天（秒）


def create_access_token(user_id: int, phone: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    
    Args:
        user_id: 用户ID
        phone: 手机号
        expires_delta: 过期时间增量（可选）
    
    Returns:
        JWT token字符串
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRES)
    
    payload = {
        'user_id': user_id,
        'phone': phone,
        'exp': expire,
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    验证访问令牌
    
    Args:
        token: JWT token字符串
    
    Returns:
        解码后的payload，如果验证失败返回None
    """
    try:
        # 移除 'Bearer ' 前缀（如果有）
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        print('Token已过期')
        return None
    except jwt.InvalidTokenError as e:
        print(f'Token无效: {e}')
        return None


def decode_token_without_verification(token: str) -> Optional[Dict[str, Any]]:
    """
    解码token但不验证（用于调试）
    
    Args:
        token: JWT token字符串
    
    Returns:
        解码后的payload
    """
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception as e:
        print(f'解码失败: {e}')
        return None


if __name__ == '__main__':
    # 测试
    print('测试 JWT Helper...')
    
    # 创建token
    token = create_access_token(user_id=1, phone='13800138000')
    print(f'生成的Token: {token[:50]}...')
    
    # 验证token
    payload = verify_access_token(token)
    if payload:
        print(f'验证成功: user_id={payload["user_id"]}, phone={payload["phone"]}')
    else:
        print('验证失败')