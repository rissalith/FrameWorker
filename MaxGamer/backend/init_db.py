"""
数据库初始化脚本
运行此脚本创建所有数据库表
"""

import sys
import os

# 添加父目录到路径，以便导入 database 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, get_db_session, User, UserQuota
from utils.password_helper import hash_password


def create_test_user():
    """创建测试用户（可选）"""
    db = get_db_session()
    try:
        # 检查是否已存在测试用户
        existing_user = db.query(User).filter(User.phone == '13800138000').first()
        if existing_user:
            print('⚠️  测试用户已存在，跳过创建')
            return
        
        # 创建测试用户
        test_user = User(
            phone='13800138000',
            password_hash=hash_password('123456'),
            nickname='测试用户',
            status='active'
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # 创建用户配额
        quota = UserQuota(
            user_id=test_user.id,
            daily_limit=100,
            daily_used=0,
            total_used=0
        )
        db.add(quota)
        db.commit()
        
        print('✅ 测试用户创建成功！')
        print(f'   手机号: {test_user.phone}')
        print(f'   密码: 123456')
        print(f'   用户ID: {test_user.id}')
        
    except Exception as e:
        print(f'❌ 创建测试用户失败: {e}')
        db.rollback()
    finally:
        db.close()


def main():
    """主函数"""
    print('=' * 60)
    print('FrameWorker 数据库初始化')
    print('=' * 60)
    
    # 初始化数据库
    init_db()
    
    # 询问是否创建测试用户
    print('\n是否创建测试用户？(y/n): ', end='')
    choice = input().strip().lower()
    
    if choice == 'y':
        create_test_user()
    
    print('\n' + '=' * 60)
    print('数据库初始化完成！')
    print('=' * 60)
    print('\n下一步:')
    print('1. 安装依赖: pip install -r requirements.txt')
    print('2. 配置环境变量: 复制 .env.example 为 .env 并配置')
    print('3. 启动服务器: python app.py')
    print()


if __name__ == '__main__':
    main()