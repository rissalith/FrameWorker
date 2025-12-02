#!/usr/bin/env python3
"""直接创建测试用户(无需验证码)"""
import sys
sys.path.insert(0, '/app')

from database import SessionLocal, User, UserQuota
from utils.password_helper import hash_password
from datetime import datetime

def create_user():
    db = SessionLocal()
    try:
        # 检查用户是否已存在
        email = 'test@xmframer.com'
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f'❌ 用户已存在: {email}')
            return
        
        # 创建新用户
        user = User(
            email=email,
            nickname='测试用户',
            password_hash=hash_password('test123456'),
            status='active',
            last_login_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # 创建用户配额
        quota = UserQuota(
            user_id=user.id,
            daily_limit=10,
            daily_used=0,
            total_used=0
        )
        db.add(quota)
        db.commit()
        
        print(f'✅ 测试用户创建成功!')
        print(f'   邮箱: {email}')
        print(f'   密码: test123456')
        print(f'   用户ID: {user.id}')
        
        # 显示所有用户
        users = db.query(User).all()
        print(f'\n📊 当前用户数: {len(users)}')
        for i, u in enumerate(users, 1):
            account = u.email or u.phone or 'N/A'
            print(f'  {i}. {account}')
    finally:
        db.close()

if __name__ == '__main__':
    create_user()