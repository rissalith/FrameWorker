#!/usr/bin/env python3
"""
初始化管理员账号脚本
在部署时运行，创建默认管理员账号
"""

import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_db_session, User, Wallet
from utils.password_helper import hash_password

def init_admin():
    """初始化管理员账号"""
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_password = os.getenv('ADMIN_PASSWORD')
    admin_nickname = os.getenv('ADMIN_NICKNAME', 'Admin')
    
    if not admin_email or not admin_password:
        print('[SKIP] 未设置 ADMIN_EMAIL 或 ADMIN_PASSWORD 环境变量，跳过管理员初始化')
        return None
    
    db = get_db_session()
    try:
        # 检查是否已存在管理员
        existing = db.query(User).filter(User.email == admin_email).first()
        
        if existing:
            # 更新为管理员角色
            if existing.role != 'admin':
                existing.role = 'admin'
                existing.password_hash = hash_password(admin_password)
                db.commit()
                print(f'[OK] 已将用户 {admin_email} 升级为管理员')
            else:
                print(f'[INFO] 管理员账号已存在: {admin_email}')
            return existing
        
        # 创建新管理员
        admin = User(
            email=admin_email,
            nickname=admin_nickname,
            password_hash=hash_password(admin_password),
            role='admin',
            status='active',
            balance=0
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        # 创建钱包
        wallet = Wallet(
            user_id=admin.id,
            balance=0
        )
        db.add(wallet)
        db.commit()
        
        print(f'[OK] 管理员账号创建成功: {admin_email}')
        return admin
        
    except Exception as e:
        print(f'[ERROR] 初始化管理员失败: {e}')
        db.rollback()
        raise
    finally:
        db.close()


def init_default_game():
    """初始化默认游戏数据"""
    from database import Game
    import json
    
    db = get_db_session()
    try:
        # 检查是否已存在
        existing = db.query(Game).filter(Game.id == 'fortune-game').first()
        if existing:
            print('[INFO] 默认游戏已存在: fortune-game')
            return existing
        
        # 创建默认游戏
        game = Game(
            id='fortune-game',
            name='巫女占卜',
            name_display='巫女占卜',
            description='AI驱动的直播互动占卜游戏，支持抖音、B站等直播平台',
            price=500,
            duration_days=30,
            status='published',
            category='直播互动',
            tags=json.dumps(['AI', '占卜', '直播', '互动']),
            index_url='/fortune-game/index.html',
            cover_url='/fortune-game/images/cover.jpg',
            sort_order=1
        )
        db.add(game)
        db.commit()
        
        print('[OK] 默认游戏创建成功: fortune-game')
        return game
        
    except Exception as e:
        print(f'[ERROR] 初始化默认游戏失败: {e}')
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == '__main__':
    print('=== 初始化系统数据 ===')
    
    # 初始化管理员
    init_admin()
    
    # 初始化默认游戏
    init_default_game()
    
    print('=== 初始化完成 ===')

