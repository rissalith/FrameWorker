#!/usr/bin/python
# coding:utf-8

"""
服务层模块
"""

from .live_service import LiveService

# 可选导入 - 这些服务需要数据库支持
try:
    from .mapping_service import MappingService
    from .game_service import GameService
    __all__ = ['LiveService', 'MappingService', 'GameService']
except ImportError:
    __all__ = ['LiveService']