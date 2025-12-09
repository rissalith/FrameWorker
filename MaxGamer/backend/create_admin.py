"""
创建管理员账号脚本
用于快速创建或更新管理员账号
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from database import get_db_session, User
from utils.password_helper import hash_password
from datetime import datetime


def create_admin_account(username='admin', password='pXw1995'):
    """
    创建管理员账号

    Args:
        username: 管理员用户名
        password: 管理员密码
    """
    db = get_db_session()

    try:
        # 检查是否已存在
        existing_user = db.query(User).filter(User.email == f'{username}@maxgamer.local').first()

        if existing_user:
            print(f'[Admin] 用户已存在: {username}')
            print(f'[Admin] 正在更新密码和角色...')

            # 更新密码和角色
            existing_user.password_hash = hash_password(password)
            existing_user.role = 'admin'
            existing_user.status = 'active'
            existing_user.updated_at = datetime.utcnow()

            db.commit()

            print(f'[SUCCESS] 管理员账号已更新!')
            print(f'   用户名: {username}')
            print(f'   邮箱: {existing_user.email}')
            print(f'   角色: {existing_user.role}')

        else:
            print(f'[Admin] 正在创建新管理员账号: {username}')

            # 创建新用户
            admin_user = User(
                email=f'{username}@maxgamer.local',
                password_hash=hash_password(password),
                nickname=username.capitalize(),
                role='admin',
                status='active',
                balance=999999,  # 给管理员一些初始积分
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(admin_user)
            db.commit()

            print(f'[SUCCESS] 管理员账号创建成功!')
            print(f'   用户名: {username}')
            print(f'   邮箱: {admin_user.email}')
            print(f'   角色: {admin_user.role}')
            print(f'   积分: {admin_user.balance}')

        print(f'\n登录信息:')
        print(f'   邮箱: {username}@maxgamer.local')
        print(f'   密码: {password}')

        return True

    except Exception as e:
        print(f'[ERROR] 创建管理员账号失败: {e}')
        import traceback
        traceback.print_exc()
        db.rollback()
        return False

    finally:
        db.close()


if __name__ == '__main__':
    print('=== MaxGamer 管理员账号创建工具 ===\n')

    # 可以从命令行参数读取（如果提供）
    if len(sys.argv) > 1:
        username = sys.argv[1]
        password = sys.argv[2] if len(sys.argv) > 2 else 'pXw1995'
    else:
        username = 'admin'
        password = 'pXw1995'

    create_admin_account(username, password)
