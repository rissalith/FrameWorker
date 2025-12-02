#!/usr/bin/env python3
"""
检查远程数据库中用户的密码状态
"""
import pymysql
import sys

# 数据库配置
DB_CONFIG = {
    'host': '149.88.69.87',
    'port': 3306,
    'user': 'xmgamer',
    'password': 'xmgamer123',  # 请替换为实际密码
    'database': 'xmgamer',
    'charset': 'utf8mb4'
}

def check_user_password(email):
    """检查用户密码状态"""
    try:
        # 连接数据库
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 查询用户信息
        sql = """
        SELECT 
            id, 
            email, 
            nickname, 
            password_hash IS NOT NULL as has_password,
            LENGTH(password_hash) as password_length,
            oauth_provider,
            oauth_id,
            created_at,
            last_login_at
        FROM users 
        WHERE email = %s
        """
        
        cursor.execute(sql, (email,))
        user = cursor.fetchone()
        
        if user:
            print(f"\n用户信息：")
            print(f"  ID: {user['id']}")
            print(f"  邮箱: {user['email']}")
            print(f"  昵称: {user['nickname']}")
            print(f"  是否设置密码: {'是' if user['has_password'] else '否'}")
            print(f"  密码哈希长度: {user['password_length'] or 0}")
            print(f"  OAuth提供商: {user['oauth_provider'] or '无'}")
            print(f"  OAuth ID: {user['oauth_id'] or '无'}")
            print(f"  创建时间: {user['created_at']}")
            print(f"  最后登录: {user['last_login_at']}")
            
            if not user['has_password']:
                print(f"\n⚠️  该用户未设置密码！")
            else:
                print(f"\n✅ 该用户已设置密码")
        else:
            print(f"\n❌ 未找到邮箱为 {email} 的用户")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ 数据库查询失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    email = 'xanderpxw@gmail.com'
    if len(sys.argv) > 1:
        email = sys.argv[1]
    
    check_user_password(email)