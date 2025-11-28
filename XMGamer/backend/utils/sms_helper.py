"""
短信验证码工具类
开发环境使用模拟发送，生产环境接入真实短信服务（阿里云SMS）
"""

import os
import random
import string
import json
from datetime import datetime, timedelta
from typing import Optional, TYPE_CHECKING

# 阿里云SMS SDK
try:
    from alibabacloud_dysmsapi20170525.client import Client as DysmsapiClient
    from alibabacloud_tea_openapi import models as open_api_models
    from alibabacloud_dysmsapi20170525 import models as dysmsapi_models
    from alibabacloud_tea_util import models as util_models
    ALIYUN_SMS_AVAILABLE = True
except ImportError:
    ALIYUN_SMS_AVAILABLE = False
    DysmsapiClient = None  # type: ignore
    open_api_models = None  # type: ignore
    dysmsapi_models = None  # type: ignore
    util_models = None  # type: ignore
    print('[WARNING] 阿里云SMS SDK未安装，请运行: pip install alibabacloud-dysmsapi20170525')


# 短信配置
SMS_CODE_EXPIRES = int(os.getenv('SMS_CODE_EXPIRES', 300))  # 验证码有效期（秒），默认5分钟
SMS_RATE_LIMIT = int(os.getenv('SMS_RATE_LIMIT', 60))  # 发送间隔（秒），默认1分钟
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')  # development 或 production

# 阿里云SMS配置
ALIYUN_ACCESS_KEY_ID = os.getenv('ALIYUN_ACCESS_KEY_ID', '')  # 阿里云AccessKeyId
ALIYUN_ACCESS_KEY_SECRET = os.getenv('ALIYUN_ACCESS_KEY_SECRET', '')  # 阿里云AccessKeySecret
ALIYUN_SMS_SIGN_NAME = os.getenv('ALIYUN_SMS_SIGN_NAME', '')  # 短信签名
ALIYUN_SMS_TEMPLATE_CODE = os.getenv('ALIYUN_SMS_TEMPLATE_CODE', '')  # 短信模板CODE
ALIYUN_SMS_ENDPOINT = os.getenv('ALIYUN_SMS_ENDPOINT', 'dysmsapi.aliyuncs.com')  # 接入点


def generate_code(length: int = 6) -> str:
    """
    生成随机验证码
    
    Args:
        length: 验证码长度，默认6位
    
    Returns:
        验证码字符串
    """
    return ''.join(random.choices(string.digits, k=length))


def send_sms_code(phone: str, code: str, purpose: str = 'login') -> bool:
    """
    发送短信验证码
    
    Args:
        phone: 手机号
        code: 验证码
        purpose: 用途（login, register, reset）
    
    Returns:
        是否发送成功
    """
    if ENVIRONMENT == 'development':
        # 开发环境：模拟发送，打印到控制台
        print('=' * 60)
        print('[SMS] 短信验证码(开发环境模拟)')
        print(f'   手机号: {phone}')
        print(f'   验证码: {code}')
        print(f'   用途: {purpose}')
        print(f'   有效期: {SMS_CODE_EXPIRES // 60} 分钟')
        print('=' * 60)
        return True
    else:
        # 生产环境：接入真实短信服务
        return send_sms_code_production(phone, code, purpose)


def create_aliyun_sms_client():
    """
    创建阿里云SMS客户端
    
    Returns:
        SMS客户端实例或None
    """
    if not ALIYUN_SMS_AVAILABLE:
        print('[ERROR] 阿里云SMS SDK未安装')
        return None
    
    if not all([ALIYUN_ACCESS_KEY_ID, ALIYUN_ACCESS_KEY_SECRET]):
        print('[ERROR] 阿里云SMS配置不完整，请检查环境变量:')
        print('  - ALIYUN_ACCESS_KEY_ID')
        print('  - ALIYUN_ACCESS_KEY_SECRET')
        return None
    
    try:
        config = open_api_models.Config(
            access_key_id=ALIYUN_ACCESS_KEY_ID,
            access_key_secret=ALIYUN_ACCESS_KEY_SECRET,
            endpoint=ALIYUN_SMS_ENDPOINT
        )
        return DysmsapiClient(config)
    except Exception as e:
        print(f'[ERROR] 创建阿里云SMS客户端失败: {e}')
        return None


def send_sms_code_production(phone: str, code: str, purpose: str) -> bool:
    """
    生产环境发送短信验证码（阿里云SMS）
    
    Args:
        phone: 手机号
        code: 验证码
        purpose: 用途
    
    Returns:
        是否发送成功
    """
    if not ALIYUN_SMS_AVAILABLE:
        print('[ERROR] 阿里云SMS SDK未安装')
        return False
    
    if not all([ALIYUN_SMS_SIGN_NAME, ALIYUN_SMS_TEMPLATE_CODE]):
        print('[ERROR] 阿里云SMS配置不完整，请检查环境变量:')
        print('  - ALIYUN_SMS_SIGN_NAME')
        print('  - ALIYUN_SMS_TEMPLATE_CODE')
        return False
    
    # 创建客户端
    client = create_aliyun_sms_client()
    if not client:
        return False
    
    try:
        # 构造请求
        request = dysmsapi_models.SendSmsRequest(
            phone_numbers=phone,
            sign_name=ALIYUN_SMS_SIGN_NAME,
            template_code=ALIYUN_SMS_TEMPLATE_CODE,
            template_param=json.dumps({
                'code': code,
                'minute': str(SMS_CODE_EXPIRES // 60)
            })
        )
        
        # 发送短信
        runtime = util_models.RuntimeOptions()
        response = client.send_sms_with_options(request, runtime)
        
        # 检查响应
        if response.body.code == 'OK':
            print(f'[OK] 短信发送成功: {phone}')
            print(f'   RequestId: {response.body.request_id}')
            print(f'   BizId: {response.body.biz_id}')
            return True
        else:
            print(f'[ERROR] 短信发送失败: {response.body.code} - {response.body.message}')
            return False
            
    except Exception as e:
        print(f'[ERROR] 阿里云SMS异常: {e}')
        return False


def validate_sms_code_format(code: str) -> bool:
    """
    验证验证码格式
    
    Args:
        code: 验证码
    
    Returns:
        格式是否正确
    """
    return code.isdigit() and len(code) == 6


if __name__ == '__main__':
    # 测试
    print('测试 SMS Helper...')
    
    # 生成验证码
    code = generate_code()
    print(f'生成的验证码: {code}')
    
    # 发送验证码
    success = send_sms_code('13800138000', code, 'login')
    print(f'发送结果: {"成功" if success else "失败"}')
    
    # 验证格式
    is_valid = validate_sms_code_format(code)
    print(f'验证码格式: {"正确" if is_valid else "错误"}')