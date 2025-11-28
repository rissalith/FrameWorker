#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将PNG精灵图转换为WebP格式
"""
from PIL import Image
import os
import sys

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def convert_png_to_webp(png_path, webp_path, quality=90):
    """
    将PNG图片转换为WebP格式
    
    Args:
        png_path: PNG文件路径
        webp_path: 输出的WebP文件路径
        quality: WebP质量 (0-100)
    """
    print(f"正在转换: {png_path}")
    
    # 打开PNG图片
    img = Image.open(png_path)
    
    # 获取图片信息
    width, height = img.size
    mode = img.mode
    print(f"  尺寸: {width}x{height}")
    print(f"  模式: {mode}")
    
    # 转换为WebP格式
    img.save(webp_path, 'WEBP', quality=quality, method=6)
    
    # 获取文件大小
    png_size = os.path.getsize(png_path) / (1024 * 1024)  # MB
    webp_size = os.path.getsize(webp_path) / (1024 * 1024)  # MB
    compression_ratio = (1 - webp_size / png_size) * 100
    
    print(f"  PNG大小: {png_size:.2f} MB")
    print(f"  WebP大小: {webp_size:.2f} MB")
    print(f"  压缩率: {compression_ratio:.1f}%")
    print(f"  [OK] 转换完成: {webp_path}\n")

def main():
    # 当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 需要转换的文件列表
    conversions = [
        {
            'input': os.path.join(current_dir, '待机-张望.png'),
            'output': os.path.join(current_dir, 'login-Max待机-张望.webp')
        },
        {
            'input': os.path.join(current_dir, '待机-常态.png'),
            'output': os.path.join(current_dir, 'login-Max待机-常态.webp')
        },
        {
            'input': os.path.join(current_dir, '待机-深呼吸.png'),
            'output': os.path.join(current_dir, 'login-Max待机-深呼吸.webp')
        }
    ]
    
    print("=" * 60)
    print("PNG to WebP 转换工具")
    print("=" * 60)
    print()
    
    for item in conversions:
        input_path = item['input']
        output_path = item['output']
        
        if not os.path.exists(input_path):
            print(f"[ERROR] 文件不存在: {input_path}\n")
            continue
        
        try:
            convert_png_to_webp(input_path, output_path, quality=90)
        except Exception as e:
            print(f"[ERROR] 转换失败: {e}\n")
    
    print("=" * 60)
    print("转换完成!")
    print("=" * 60)

if __name__ == '__main__':
    main()