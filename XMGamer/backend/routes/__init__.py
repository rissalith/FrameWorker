"""
API路由模块
"""

from .auth import auth_bp
from .history import history_bp

__all__ = ['auth_bp', 'history_bp']