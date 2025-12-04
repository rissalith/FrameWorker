"""
游戏会话管理器
负责管理用户的游戏服务实例，实现按需启动和自动清理
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from collections import defaultdict


class GameSession:
    """游戏会话"""
    
    def __init__(self, user_id: str, game_id: str, session_id: str):
        self.user_id = user_id
        self.game_id = game_id
        self.session_id = session_id
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.services = {}  # 存储游戏服务实例
        self.data = {}  # 存储会话数据
        self.lock = threading.Lock()
    
    def update_activity(self):
        """更新最后活动时间"""
        with self.lock:
            self.last_activity = datetime.utcnow()
    
    def is_expired(self, timeout_minutes: int = 30) -> bool:
        """检查会话是否过期"""
        with self.lock:
            timeout = timedelta(minutes=timeout_minutes)
            return datetime.utcnow() - self.last_activity > timeout
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """获取服务实例"""
        with self.lock:
            return self.services.get(service_name)
    
    def set_service(self, service_name: str, service_instance: Any):
        """设置服务实例"""
        with self.lock:
            self.services[service_name] = service_instance
    
    def cleanup(self):
        """清理会话资源"""
        with self.lock:
            # 清理所有服务
            for service_name, service in self.services.items():
                try:
                    # 如果服务有cleanup方法，调用它
                    if hasattr(service, 'cleanup'):
                        service.cleanup()
                    # 如果服务有stop方法，调用它
                    elif hasattr(service, 'stop'):
                        service.stop()
                    print(f'[GameSession] 清理服务: {service_name}')
                except Exception as e:
                    print(f'[GameSession] 清理服务失败 {service_name}: {e}')
            
            self.services.clear()
            self.data.clear()


class GameSessionManager:
    """游戏会话管理器"""
    
    def __init__(self, session_timeout: int = 30, cleanup_interval: int = 5):
        """
        初始化会话管理器
        
        Args:
            session_timeout: 会话超时时间（分钟）
            cleanup_interval: 清理检查间隔（分钟）
        """
        self.sessions: Dict[str, GameSession] = {}  # session_id -> GameSession
        self.user_sessions: Dict[str, Dict[str, str]] = defaultdict(dict)  # user_id -> {game_id -> session_id}
        self.session_timeout = session_timeout
        self.cleanup_interval = cleanup_interval
        self.lock = threading.Lock()
        self.cleanup_thread = None
        self.running = False
    
    def start(self):
        """启动会话管理器"""
        if not self.running:
            self.running = True
            self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self.cleanup_thread.start()
            print(f'[GameSessionManager] 已启动，会话超时: {self.session_timeout}分钟')
    
    def stop(self):
        """停止会话管理器"""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        
        # 清理所有会话
        with self.lock:
            for session in list(self.sessions.values()):
                session.cleanup()
            self.sessions.clear()
            self.user_sessions.clear()
        
        print('[GameSessionManager] 已停止')
    
    def create_session(self, user_id: str, game_id: str) -> GameSession:
        """
        创建或获取用户的游戏会话
        
        Args:
            user_id: 用户ID
            game_id: 游戏ID
            
        Returns:
            GameSession: 游戏会话实例
        """
        with self.lock:
            # 检查用户是否已有该游戏的会话
            if user_id in self.user_sessions and game_id in self.user_sessions[user_id]:
                session_id = self.user_sessions[user_id][game_id]
                session = self.sessions.get(session_id)
                
                if session and not session.is_expired(self.session_timeout):
                    # 会话存在且未过期，更新活动时间
                    session.update_activity()
                    print(f'[GameSessionManager] 复用会话: user={user_id}, game={game_id}, session={session_id}')
                    return session
                else:
                    # 会话已过期，清理旧会话
                    if session:
                        session.cleanup()
                        del self.sessions[session_id]
                    del self.user_sessions[user_id][game_id]
            
            # 创建新会话
            session_id = f"{user_id}_{game_id}_{int(time.time() * 1000)}"
            session = GameSession(user_id, game_id, session_id)
            
            self.sessions[session_id] = session
            self.user_sessions[user_id][game_id] = session_id
            
            print(f'[GameSessionManager] 创建新会话: user={user_id}, game={game_id}, session={session_id}')
            return session
    
    def get_session(self, session_id: str) -> Optional[GameSession]:
        """获取会话"""
        with self.lock:
            session = self.sessions.get(session_id)
            if session and not session.is_expired(self.session_timeout):
                session.update_activity()
                return session
            return None
    
    def get_user_session(self, user_id: str, game_id: str) -> Optional[GameSession]:
        """获取用户的游戏会话"""
        with self.lock:
            if user_id in self.user_sessions and game_id in self.user_sessions[user_id]:
                session_id = self.user_sessions[user_id][game_id]
                return self.get_session(session_id)
            return None
    
    def close_session(self, session_id: str):
        """关闭会话"""
        with self.lock:
            session = self.sessions.get(session_id)
            if session:
                session.cleanup()
                del self.sessions[session_id]
                
                # 从用户会话映射中移除
                user_id = session.user_id
                game_id = session.game_id
                if user_id in self.user_sessions and game_id in self.user_sessions[user_id]:
                    del self.user_sessions[user_id][game_id]
                    if not self.user_sessions[user_id]:
                        del self.user_sessions[user_id]
                
                print(f'[GameSessionManager] 关闭会话: {session_id}')
    
    def close_user_session(self, user_id: str, game_id: str):
        """关闭用户的游戏会话"""
        with self.lock:
            if user_id in self.user_sessions and game_id in self.user_sessions[user_id]:
                session_id = self.user_sessions[user_id][game_id]
                self.close_session(session_id)
    
    def get_session_count(self) -> int:
        """获取当前会话数量"""
        with self.lock:
            return len(self.sessions)
    
    def get_user_session_count(self, user_id: str) -> int:
        """获取用户的会话数量"""
        with self.lock:
            return len(self.user_sessions.get(user_id, {}))
    
    def _cleanup_loop(self):
        """清理循环"""
        while self.running:
            try:
                time.sleep(self.cleanup_interval * 60)  # 转换为秒
                self._cleanup_expired_sessions()
            except Exception as e:
                print(f'[GameSessionManager] 清理循环错误: {e}')
    
    def _cleanup_expired_sessions(self):
        """清理过期会话"""
        with self.lock:
            expired_sessions = [
                session_id for session_id, session in self.sessions.items()
                if session.is_expired(self.session_timeout)
            ]
            
            for session_id in expired_sessions:
                session = self.sessions[session_id]
                print(f'[GameSessionManager] 清理过期会话: user={session.user_id}, game={session.game_id}, session={session_id}')
                
                session.cleanup()
                del self.sessions[session_id]
                
                # 从用户会话映射中移除
                user_id = session.user_id
                game_id = session.game_id
                if user_id in self.user_sessions and game_id in self.user_sessions[user_id]:
                    del self.user_sessions[user_id][game_id]
                    if not self.user_sessions[user_id]:
                        del self.user_sessions[user_id]
            
            if expired_sessions:
                print(f'[GameSessionManager] 已清理 {len(expired_sessions)} 个过期会话')


# 创建全局会话管理器实例
game_session_manager = GameSessionManager(
    session_timeout=30,  # 30分钟超时
    cleanup_interval=5   # 每5分钟检查一次
)