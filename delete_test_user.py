#!/usr/bin/env python3
"""删除测试用户脚本"""
import sys
sys.path.insert(0, '/app')

from database import SessionLocal, User

def delete_user():
    db = SessionLocal()
    try:
        # 删除邮箱用户
        user = db.query(User).filter(User.email == 'xanderpxw@gmail.com').first()
        if user:
            db.delete(user)
            db.commit()
            print('✅ 邮箱用户已删除: xanderpxw@gmail.com')
        else:
            print('❌ 用户不存在: xanderpxw@gmail.com')
        
        # 显示剩余用户
        users = db.query(User).all()
        print(f'\n📊 当前用户数: {len(users)}')
        for i, u in enumerate(users, 1):
            account = u.email or u.phone or 'N/A'
            print(f'  {i}. {account}')
    finally:
        db.close()

if __name__ == '__main__':
    delete_user()