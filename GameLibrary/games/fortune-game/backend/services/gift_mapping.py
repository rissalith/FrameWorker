#!/usr/bin/python
# coding:utf-8

"""
礼物名称映射配置
将抖音直播间的礼物名称映射到游戏中的运势类型
"""

# 礼物名称到运势类型的映射
GIFT_TO_FORTUNE_TYPE = {
    '小心心': 'daily',     # 日常运势
    '鲜花': 'love',        # 爱情运势
    '棒棒糖': 'wealth',    # 财富运势
    '大啤酒': 'health',    # 健康运势
    'Thuglife': 'career'   # 事业运势
}

def get_fortune_type_by_gift(gift_name):
    """
    根据礼物名称获取对应的运势类型
    
    Args:
        gift_name: 礼物名称
        
    Returns:
        str: 运势类型 (love/daily/career/health/wealth)，如果不匹配则返回None
    """
    return GIFT_TO_FORTUNE_TYPE.get(gift_name)

def is_valid_gift(gift_name):
    """
    检查礼物名称是否在映射表中
    
    Args:
        gift_name: 礼物名称
        
    Returns:
        bool: 是否是有效的礼物
    """
    return gift_name in GIFT_TO_FORTUNE_TYPE