#!/usr/bin/env python3
"""
点数系统数据库初始化脚本
创建表并插入初始商品数据
"""

import sys
import os
import json

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, get_db_session, Product, Wallet
from datetime import datetime


def init_products():
    """初始化商品数据"""
    db = get_db_session()
    try:
        print('\n正在初始化商品数据...')
        
        # 充值套餐
        recharge_products = [
            {
                'id': 'recharge_100',
                'name': '100点数',
                'description': '基础充值套餐',
                'category': 'recharge',
                'game_id': None,
                'price': 100,
                'price_cny': 9.99,
                'duration_days': None,
                'features': '[]',
                'is_active': True,
                'sort_order': 1
            },
            {
                'id': 'recharge_550',
                'name': '550点数',
                'description': '热门充值套餐，额外赠送10%',
                'category': 'recharge',
                'game_id': None,
                'price': 550,
                'price_cny': 49.99,
                'duration_days': None,
                'features': '[]',
                'is_active': True,
                'sort_order': 2
            },
            {
                'id': 'recharge_1200',
                'name': '1200点数',
                'description': '超值充值套餐，额外赠送20%',
                'category': 'recharge',
                'game_id': None,
                'price': 1200,
                'price_cny': 99.99,
                'duration_days': None,
                'features': '[]',
                'is_active': True,
                'sort_order': 3
            }
        ]
        
        # 巫女占卜游戏套餐
        fortune_products = [
            {
                'id': 'fortune_1d',
                'name': '巫女占卜-1天体验',
                'description': '体验版，适合新用户试用',
                'category': 'game',
                'game_id': 'fortune-game',
                'price': 50,
                'price_cny': None,
                'duration_days': 1,
                'features': '[]',
                'is_active': True,
                'sort_order': 1
            },
            {
                'id': 'fortune_7d',
                'name': '巫女占卜-7天',
                'description': '周卡，性价比之选',
                'category': 'game',
                'game_id': 'fortune-game',
                'price': 300,
                'price_cny': None,
                'duration_days': 7,
                'features': '[]',
                'is_active': True,
                'sort_order': 2
            },
            {
                'id': 'fortune_30d',
                'name': '巫女占卜-30天',
                'description': '月卡，最受欢迎',
                'category': 'game',
                'game_id': 'fortune-game',
                'price': 500,
                'price_cny': None,
                'duration_days': 30,
                'features': '[]',
                'is_active': True,
                'sort_order': 3
            },
            {
                'id': 'fortune_90d',
                'name': '巫女占卜-90天',
                'description': '季卡，超值优惠',
                'category': 'game',
                'game_id': 'fortune-game',
                'price': 1500,
                'price_cny': None,
                'duration_days': 90,
                'features': '[]',
                'is_active': True,
                'sort_order': 4
            },
            {
                'id': 'fortune_perm',
                'name': '巫女占卜-永久版',
                'description': '一次购买，永久使用',
                'category': 'game',
                'game_id': 'fortune-game',
                'price': 3000,
                'price_cny': None,
                'duration_days': None,
                'features': '[]',
                'is_active': True,
                'sort_order': 5
            }
        ]
        
        # 增值功能
        feature_products = [
            {
                'id': 'fortune_nowm',
                'name': '去水印',
                'description': '移除游戏界面水印',
                'category': 'feature',
                'game_id': 'fortune-game',
                'price': 200,
                'price_cny': None,
                'duration_days': None,
                'features': '["no_watermark"]',
                'is_active': True,
                'sort_order': 1
            },
            {
                'id': 'fortune_ai_pack',
                'name': 'AI对话包',
                'description': '解锁高级AI对话功能',
                'category': 'feature',
                'game_id': 'fortune-game',
                'price': 100,
                'price_cny': None,
                'duration_days': None,
                'features': '["ai_enabled"]',
                'is_active': True,
                'sort_order': 2
            },
            {
                'id': 'fortune_effects',
                'name': '高级特效包',
                'description': '解锁更多视觉特效',
                'category': 'feature',
                'game_id': 'fortune-game',
                'price': 300,
                'price_cny': None,
                'duration_days': None,
                'features': '["advanced_effects"]',
                'is_active': True,
                'sort_order': 3
            }
        ]
        
        all_products = recharge_products + fortune_products + feature_products
        
        # 插入商品
        for product_data in all_products:
            existing = db.query(Product).filter(Product.id == product_data['id']).first()
            if not existing:
                product = Product(**product_data)
                db.add(product)
                print(f'  ✓ 添加商品: {product_data["name"]}')
            else:
                print(f'  - 商品已存在: {product_data["name"]}')
        
        db.commit()
        print(f'[OK] 商品数据初始化完成! 共 {len(all_products)} 个商品')
        
    except Exception as e:
        print(f'[ERROR] 初始化商品数据失败: {e}')
        db.rollback()
        raise e
    finally:
        db.close()


def create_test_wallet():
    """为测试用户创建钱包"""
    db = get_db_session()
    try:
        print('\n正在创建测试钱包...')
        
        # 检查是否有用户
        from database import User
        users = db.query(User).limit(5).all()
        
        if not users:
            print('  - 没有找到用户，跳过钱包创建')
            return
        
        for user in users:
            existing_wallet = db.query(Wallet).filter(Wallet.user_id == user.id).first()
            if not existing_wallet:
                wallet = Wallet(
                    user_id=user.id,
                    balance=0,
                    frozen_balance=0,
                    total_recharged=0,
                    total_consumed=0
                )
                db.add(wallet)
                print(f'  ✓ 为用户 {user.id} ({user.nickname}) 创建钱包')
            else:
                print(f'  - 用户 {user.id} ({user.nickname}) 已有钱包')
        
        db.commit()
        print('[OK] 测试钱包创建完成!')
        
    except Exception as e:
        print(f'[ERROR] 创建测试钱包失败: {e}')
        db.rollback()
    finally:
        db.close()


def main():
    """主函数"""
    print('=' * 60)
    print('XMGamer 点数系统初始化')
    print('=' * 60)
    
    # 1. 初始化数据库表
    init_db()
    
    # 2. 初始化商品数据
    init_products()
    
    # 3. 创建测试钱包
    create_test_wallet()
    
    print('\n' + '=' * 60)
    print('[OK] 点数系统初始化完成!')
    print('=' * 60)
    print('\n下一步:')
    print('  1. 启动后端服务: python app.py')
    print('  2. 访问 http://localhost:3000')
    print('  3. 登录后即可使用点数系统')
    print()


if __name__ == '__main__':
    main()