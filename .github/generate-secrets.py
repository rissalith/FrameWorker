#!/usr/bin/env python3
"""
GitHub Secrets 生成工具
用于生成部署所需的强随机密钥
"""

import secrets
import string

def generate_password(length=24):
    """生成强随机密码"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_secret_key(length=32):
    """生成 URL 安全的密钥"""
    return secrets.token_urlsafe(length)

def main():
    print("=" * 60)
    print("GitHub Secrets 生成工具")
    print("=" * 60)
    print()
    
    secrets_config = {
        "数据库配置": {
            "MYSQL_ROOT_PASSWORD": generate_password(24),
            "MYSQL_DATABASE": "xmgamer",
            "MYSQL_USER": "xmgamer_user",
            "MYSQL_PASSWORD": generate_password(24),
        },
        "Redis 配置": {
            "REDIS_PASSWORD": generate_password(24),
        },
        "Flask 应用配置": {
            "SECRET_KEY": generate_secret_key(32),
            "JWT_SECRET_KEY": generate_secret_key(32),
        },
        "域名配置": {
            "DOMAIN": "xmgamer.com",
            "API_DOMAIN": "api.xmgamer.com",
            "GAME_WITCH_DOMAIN": "play-witch.xmgamer.com",
            "CORS_ORIGINS": "https://xmgamer.com,https://api.xmgamer.com,https://play-witch.xmgamer.com",
        },
        "服务器配置（需要手动填写）": {
            "SERVER_HOST": "YOUR_SERVER_IP",
            "SERVER_USER": "root",
            "SERVER_SSH_KEY": "YOUR_SSH_PRIVATE_KEY",
            "SERVER_PORT": "22",
            "DEPLOY_PATH": "/var/www/FrameWorker",
        },
        "AI API 配置（需要手动填写）": {
            "DEEPSEEK_API_KEY": "sk-YOUR_DEEPSEEK_API_KEY",
            "GEMINI_API_KEY": "YOUR_GEMINI_API_KEY",
        },
    }
    
    # 打印配置
    for category, secrets in secrets_config.items():
        print(f"\n## {category}")
        print("-" * 60)
        for key, value in secrets.items():
            print(f"{key}={value}")
    
    print("\n" + "=" * 60)
    print("配置说明：")
    print("=" * 60)
    print()
    print("1. 复制上述配置到 GitHub Secrets")
    print("2. 访问: https://github.com/rissalith/FrameWorker/settings/secrets/actions")
    print("3. 点击 'New repository secret' 逐个添加")
    print("4. 将标记为 'YOUR_*' 的值替换为实际值")
    print()
    print("详细配置指南请参考: .github/SECRETS_SETUP.md")
    print()
    
    # 生成 .env 文件示例
    print("\n" + "=" * 60)
    print("生成本地 .env 文件")
    print("=" * 60)
    
    env_content = []
    for category, secrets in secrets_config.items():
        env_content.append(f"\n# {category}")
        for key, value in secrets.items():
            env_content.append(f"{key}={value}")
    
    with open('.env.generated', 'w', encoding='utf-8') as f:
        f.write('\n'.join(env_content))
    
    print("\n✅ 已生成 .env.generated 文件")
    print("⚠️  请检查并重命名为 .env 后使用")
    print("⚠️  不要将 .env 文件提交到 Git！")

if __name__ == "__main__":
    main()