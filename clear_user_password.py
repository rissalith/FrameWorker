#!/usr/bin/env python3
"""
清空指定用户的密码
"""
import pymysql
import sys

# 数据库配置
DB_CONFIG = {
    'host': '149.88.69.87',
    'port': 3306,
    'user': 'xmgamer',
    'password': 'xmgamer123',
    'database': 'xmgamer',
    'charset': 'utf8mb4'
}

def clear_password(email):
    """清空用户密码"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        # 先查询用户当前状态
        cursor.execute("""
            SELECT id, email, nickname, 
                   password_hash IS NOT NULL as has_password,
                   LENGTH(password_hash) as password_length
            FROM users WHERE email = %s
        """, (email,))
        
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ 未找到邮箱为 {email} 的用户")
            return
        
        print(f"\n当前用户状态：")
        print(f"  ID: {user['id']}")
        print(f"  邮箱: {user['email']}")
        print(f"  昵称: {user['nickname']}")
        print(f"  是否有密码: {'是' if user['has_password'] else '否'}")
        print(f"  密码长度: {user['password_length'] or 0}")
        
        if not user['has_password']:
            print(f"\n✅ 该用户本来就没有密码，无需清空")
            return
        
        # 清空密码
        cursor.execute("UPDATE users SET password_hash = NULL WHERE email = %s", (email,))
        conn.commit()
        
        print(f"\n✅ 已成功清空用户密码！")
        print(f"现在该用户通过第三方登录时应该会弹出设置密码界面")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ 操作失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    email = 'xanderpxw@gmail.com'
    if len(sys.argv) > 1:
        email = sys.argv[1]
    
    clear_password(email)