"""
邮件验证码工具类
支持多种邮件发送方式：
- 开发环境：模拟发送（打印到控制台）
- SMTP：Gmail等SMTP服务
- SendGrid：专业邮件服务（推荐）
"""

import os
import random
import string
import smtplib
import socks
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Optional

# 邮件配置
EMAIL_CODE_EXPIRES = int(os.getenv('EMAIL_CODE_EXPIRES', 300))  # 验证码有效期（秒），默认5分钟
EMAIL_RATE_LIMIT = int(os.getenv('EMAIL_RATE_LIMIT', 60))  # 发送间隔（秒），默认1分钟
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')  # development 或 production
EMAIL_SERVICE = os.getenv('EMAIL_SERVICE', 'smtp')  # smtp 或 sendgrid

# SMTP配置
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')  # SMTP服务器
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))  # SMTP端口
SMTP_USER = os.getenv('SMTP_USER', '')  # 发件人邮箱
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')  # 邮箱密码或应用专用密码
SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'XMGamer')  # 发件人名称

# SendGrid配置
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')  # SendGrid API密钥
SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL', '')  # 发件人邮箱
SENDGRID_FROM_NAME = os.getenv('SENDGRID_FROM_NAME', 'XMGamer')  # 发件人名称


def generate_code(length: int = 6) -> str:
    """
    生成随机验证码
    
    Args:
        length: 验证码长度，默认6位
    
    Returns:
        验证码字符串
    """
    return ''.join(random.choices(string.digits, k=length))


def send_email_code(email: str, code: str, purpose: str = 'login') -> bool:
    """
    发送邮箱验证码
    
    Args:
        email: 邮箱地址
        code: 验证码
        purpose: 用途（login, register, reset）
    
    Returns:
        是否发送成功
    """
    if ENVIRONMENT == 'development':
        # 开发环境：模拟发送，打印到控制台
        print('=' * 60)
        print('[EMAIL] 邮箱验证码(开发环境模拟)')
        print(f'   收件人: {email}')
        print(f'   验证码: {code}')
        print(f'   用途: {purpose}')
        print(f'   有效期: {EMAIL_CODE_EXPIRES // 60} 分钟')
        print('=' * 60)
        return True
    else:
        # 生产环境：根据配置选择邮件服务
        if EMAIL_SERVICE == 'sendgrid':
            return send_email_code_sendgrid(email, code, purpose)
        else:
            return send_email_code_smtp(email, code, purpose)


def send_email_code_sendgrid(email: str, code: str, purpose: str) -> bool:
    """
    使用SendGrid发送邮箱验证码
    
    Args:
        email: 邮箱地址
        code: 验证码
        purpose: 用途
    
    Returns:
        是否发送成功
    """
    if not SENDGRID_API_KEY or not SENDGRID_FROM_EMAIL:
        print('[ERROR] SendGrid配置不完整，请检查环境变量:')
        print('  - SENDGRID_API_KEY')
        print('  - SENDGRID_FROM_EMAIL')
        return False
    
    try:
        # 导入SendGrid库
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail, Email, To, Content
        except ImportError:
            print('[ERROR] 未安装sendgrid库，请运行: pip install sendgrid')
            return False
        
        # 根据用途设置邮件主题和内容
        purpose_map = {
            'login': '登录',
            'register': '注册',
            'reset': '重置密码'
        }
        purpose_text = purpose_map.get(purpose, '验证')
        
        # 邮件内容（HTML格式）
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 8px 8px;
                }}
                .code-box {{
                    background: white;
                    border: 2px dashed #667eea;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                    margin: 20px 0;
                }}
                .code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #667eea;
                    letter-spacing: 5px;
                }}
                .footer {{
                    text-align: center;
                    color: #999;
                    font-size: 12px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎬 XMGamer</h1>
                    <p>{purpose_text}验证码</p>
                </div>
                <div class="content">
                    <p>您好，</p>
                    <p>您正在进行<strong>{purpose_text}</strong>操作，验证码为：</p>
                    <div class="code-box">
                        <div class="code">{code}</div>
                    </div>
                    <p>验证码有效期为 <strong>{EMAIL_CODE_EXPIRES // 60} 分钟</strong>，请尽快使用。</p>
                    <p>如果这不是您本人的操作，请忽略此邮件。</p>
                    <div class="footer">
                        <p>此邮件由系统自动发送，请勿回复</p>
                        <p>© 2025 XMGamer. All rights reserved.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 创建邮件
        message = Mail(
            from_email=Email(SENDGRID_FROM_EMAIL, SENDGRID_FROM_NAME),
            to_emails=To(email),
            subject=f'【XMGamer】{purpose_text}验证码',
            html_content=Content("text/html", html_content)
        )
        
        # 发送邮件
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        if response.status_code in [200, 201, 202]:
            print(f'[OK] SendGrid邮件发送成功: {email}')
            return True
        else:
            print(f'[ERROR] SendGrid返回错误: {response.status_code}')
            print(f'[ERROR] 响应内容: {response.body}')
            return False
        
    except Exception as e:
        print(f'[ERROR] SendGrid邮件发送失败: {e}')
        import traceback
        traceback.print_exc()
        return False


def send_email_code_smtp(email: str, code: str, purpose: str) -> bool:
    """
    使用SMTP发送邮箱验证码（Gmail等）
    
    Args:
        email: 邮箱地址
        code: 验证码
        purpose: 用途
    
    Returns:
        是否发送成功
    """
    if not all([SMTP_HOST, SMTP_USER, SMTP_PASSWORD]):
        print('[ERROR] SMTP配置不完整，请检查环境变量:')
        print('  - SMTP_HOST')
        print('  - SMTP_USER')
        print('  - SMTP_PASSWORD')
        return False
    
    # 检查是否需要使用代理
    proxy_url = os.getenv('PROXY_URL', '')
    use_proxy = bool(proxy_url and proxy_url.strip())
    original_socket = None
    
    try:
        # 如果配置了代理，设置SOCKS代理
        if use_proxy:
            print(f'[INFO] 使用代理: {proxy_url}')
            # 保存原始socket
            original_socket = socket.socket
            
            # 解析代理URL
            if proxy_url.startswith('http://'):
                proxy_host = proxy_url.replace('http://', '').split(':')[0]
                proxy_port = int(proxy_url.replace('http://', '').split(':')[1])
                # 设置SOCKS5代理
                socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port)
                socket.socket = socks.socksocket
            elif proxy_url.startswith('socks5://'):
                proxy_host = proxy_url.replace('socks5://', '').split(':')[0]
                proxy_port = int(proxy_url.replace('socks5://', '').split(':')[1])
                socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port)
                socket.socket = socks.socksocket
        # 根据用途设置邮件主题和内容
        purpose_map = {
            'login': '登录',
            'register': '注册',
            'reset': '重置密码'
        }
        purpose_text = purpose_map.get(purpose, '验证')
        
        # 创建邮件
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'【XMGamer】{purpose_text}验证码'
        msg['From'] = f'{SMTP_FROM_NAME} <{SMTP_USER}>'
        msg['To'] = email
        
        # 邮件内容（HTML格式）
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 8px 8px;
                }}
                .code-box {{
                    background: white;
                    border: 2px dashed #667eea;
                    border-radius: 8px;
                    padding: 20px;
                    text-align: center;
                    margin: 20px 0;
                }}
                .code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #667eea;
                    letter-spacing: 5px;
                }}
                .footer {{
                    text-align: center;
                    color: #999;
                    font-size: 12px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎬 XMGamer</h1>
                    <p>{purpose_text}验证码</p>
                </div>
                <div class="content">
                    <p>您好，</p>
                    <p>您正在进行<strong>{purpose_text}</strong>操作，验证码为：</p>
                    <div class="code-box">
                        <div class="code">{code}</div>
                    </div>
                    <p>验证码有效期为 <strong>{EMAIL_CODE_EXPIRES // 60} 分钟</strong>，请尽快使用。</p>
                    <p>如果这不是您本人的操作，请忽略此邮件。</p>
                    <div class="footer">
                        <p>此邮件由系统自动发送，请勿回复</p>
                        <p>© 2025 XMGamer. All rights reserved.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # 添加HTML内容
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # 连接SMTP服务器并发送
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()  # 启用TLS加密
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f'[OK] 邮件发送成功: {email}')
        return True
        
    except Exception as e:
        print(f'[ERROR] 邮件发送失败: {e}')
        if use_proxy:
            print('[提示] 如果使用代理失败，请检查:')
            print('  1. 代理服务是否正在运行')
            print('  2. 代理地址和端口是否正确')
            print('  3. 尝试安装 PySocks: pip install PySocks')
        return False
    finally:
        # 恢复原始socket
        if use_proxy and original_socket:
            socket.socket = original_socket


def validate_email_format(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
    
    Returns:
        格式是否正确
    """
    import re
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(pattern, email))


if __name__ == '__main__':
    # 测试
    print('测试 Email Helper...')
    
    # 生成验证码
    code = generate_code()
    print(f'生成的验证码: {code}')
    
    # 发送验证码
    success = send_email_code('test@example.com', code, 'login')
    print(f'发送结果: {"成功" if success else "失败"}')
    
    # 验证格式
    is_valid = validate_email_format('test@example.com')
    print(f'邮箱格式: {"正确" if is_valid else "错误"}')