import requests
import os

client_id = os.getenv('GOOGLE_CLIENT_ID')
client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
redirect_uri = 'http://www.xmframer.com/oauth-callback.html'

print('Client ID:', client_id)
print('Client Secret:', client_secret[:20] + '...' if client_secret else 'None')
print('Redirect URI:', redirect_uri)

# 测试token交换（使用假的code）
token_url = 'https://oauth2.googleapis.com/token'
token_data = {
    'code': 'test_code',
    'client_id': client_id,
    'client_secret': client_secret,
    'redirect_uri': redirect_uri,
    'grant_type': 'authorization_code'
}

try:
    response = requests.post(token_url, data=token_data)
    print('\n响应状态码:', response.status_code)
    print('响应内容:', response.json())
except Exception as e:
    print('错误:', e)