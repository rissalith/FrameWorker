#!/usr/bin/python
# coding:utf-8

"""
持久化连接管理器 - 管理抖音直播间的持久连接
"""

import threading
import time
import queue
from .live_monitor import LiveRoomMonitor


class PersistentConnectionManager:
    """持久化连接管理器 - 保持直播间连接始终活跃"""
    
    def __init__(self):
        """初始化连接管理器"""
        self.connections = {}  # {live_id: ConnectionInfo}
        self.lock = threading.Lock()
        self.running = True
        
        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_connections, daemon=True)
        self.monitor_thread.start()
        print("【√】持久化连接管理器已启动")
    
    def add_connection(self, live_id, message_queue):
        """
        添加或恢复一个直播间连接
        
        Args:
            live_id: 直播间ID
            message_queue: 消息队列
            
        Returns:
            bool: 是否成功添加
        """
        live_id = str(live_id)
        
        with self.lock:
            # 如果连接已存在且活跃，直接返回
            if live_id in self.connections:
                conn_info = self.connections[live_id]
                if conn_info['active']:
                    print(f"【√】直播间 {live_id} 连接已存在且活跃")
                    return True
                else:
                    print(f"【!】直播间 {live_id} 连接存在但不活跃，将重新连接")
            
            # 创建新的连接信息
            conn_info = {
                'live_id': live_id,
                'message_queue': message_queue,
                'monitor': None,
                'thread': None,
                'active': False,
                'reconnect_count': 0,
                'last_reconnect_time': 0,
                'last_message_time': time.time(),
                'should_reconnect': True  # 标记是否应该重连
            }
            
            self.connections[live_id] = conn_info
            
            # 启动连接 - 如果失败会抛出异常
            try:
                self._start_connection(live_id)
                return True
            except Exception as e:
                # 连接失败，清理资源
                print(f"【X】添加连接失败: {e}")
                if live_id in self.connections:
                    del self.connections[live_id]
                raise  # 重新抛出异常，让上层处理
    
    def remove_connection(self, live_id):
        """
        移除一个直播间连接
        
        Args:
            live_id: 直播间ID
        """
        live_id = str(live_id)
        
        with self.lock:
            if live_id not in self.connections:
                print(f"【!】直播间 {live_id} 连接不存在")
                return
            
            conn_info = self.connections[live_id]
            
            # 标记不再重连
            conn_info['should_reconnect'] = False
            
            # 停止监听器
            if conn_info['monitor']:
                try:
                    conn_info['monitor'].stop()
                    print(f"【√】已停止直播间 {live_id} 的监听器")
                except Exception as e:
                    print(f"【!】停止监听器时出错: {e}")
            
            # 移除连接
            del self.connections[live_id]
            print(f"【√】已移除直播间 {live_id} 的连接")
    
    def get_connection_status(self, live_id):
        """
        获取连接状态
        
        Args:
            live_id: 直播间ID
            
        Returns:
            dict: 连接状态信息
        """
        live_id = str(live_id)
        
        with self.lock:
            if live_id not in self.connections:
                return {'exists': False}
            
            conn_info = self.connections[live_id]
            return {
                'exists': True,
                'active': conn_info['active'],
                'reconnect_count': conn_info['reconnect_count'],
                'last_message_time': conn_info['last_message_time']
            }
    
    def get_all_connections(self):
        """
        获取所有连接的状态
        
        Returns:
            dict: 所有连接的状态
        """
        with self.lock:
            return {
                live_id: {
                    'active': info['active'],
                    'reconnect_count': info['reconnect_count'],
                    'last_message_time': info['last_message_time']
                }
                for live_id, info in self.connections.items()
            }
    
    def update_message_time(self, live_id):
        """
        更新最后消息时间
        
        Args:
            live_id: 直播间ID
        """
        live_id = str(live_id)
        
        with self.lock:
            if live_id in self.connections:
                self.connections[live_id]['last_message_time'] = time.time()
    
    def _start_connection(self, live_id):
        """
        启动一个连接（内部方法，需要在lock内调用）
        
        Args:
            live_id: 直播间ID
        """
        if live_id not in self.connections:
            return
        
        conn_info = self.connections[live_id]
        
        try:
            # 创建监听器
            monitor = LiveRoomMonitor(
                live_id,
                conn_info['message_queue']
            )
            
            conn_info['monitor'] = monitor
            
            # 先检查直播间状态
            print(f"【√】正在检查直播间 {live_id} 的状态...")
            try:
                room_status_data = monitor.get_room_status_data()
                if room_status_data is None:
                    raise Exception("无法获取直播间状态")
                
                room_status = room_status_data.get('room_status')
                if room_status == 2:
                    raise Exception("直播间未开播或已结束")
                elif room_status != 0:
                    raise Exception(f"直播间状态异常: {room_status}")
                
                print(f"【√】直播间 {live_id} 正在直播中，准备连接")
            except Exception as e:
                print(f"【X】直播间 {live_id} 状态检查失败: {e}")
                conn_info['active'] = False
                raise
            
            # 启动监听线程
            def run_monitor():
                try:
                    print(f"【√】开始连接直播间 {live_id}")
                    conn_info['active'] = True
                    monitor.start()
                except Exception as e:
                    print(f"【X】直播间 {live_id} 连接异常: {e}")
                    import traceback
                    traceback.print_exc()
                finally:
                    conn_info['active'] = False
                    print(f"【!】直播间 {live_id} 连接已断开")
            
            thread = threading.Thread(target=run_monitor, daemon=True)
            thread.start()
            conn_info['thread'] = thread
            
            print(f"【√】直播间 {live_id} 连接线程已启动")
            
        except Exception as e:
            print(f"【X】启动直播间 {live_id} 连接失败: {e}")
            import traceback
            traceback.print_exc()
            conn_info['active'] = False
            raise
    
    def _monitor_connections(self):
        """
        监控所有连接的健康状态，自动重连断开的连接
        """
        print("【√】连接监控线程已启动")
        
        while self.running:
            try:
                time.sleep(5)  # 每5秒检查一次
                
                with self.lock:
                    current_time = time.time()
                    
                    for live_id, conn_info in list(self.connections.items()):
                        # 检查是否应该重连
                        if not conn_info['should_reconnect']:
                            continue
                        
                        # 如果连接不活跃，尝试重连
                        if not conn_info['active']:
                            # 计算重连延迟（指数退避）
                            reconnect_delay = min(2 ** conn_info['reconnect_count'], 60)
                            
                            if current_time - conn_info['last_reconnect_time'] >= reconnect_delay:
                                print(f"【!】检测到直播间 {live_id} 连接断开，尝试重连（第 {conn_info['reconnect_count'] + 1} 次）")
                                
                                conn_info['reconnect_count'] += 1
                                conn_info['last_reconnect_time'] = current_time
                                
                                # 重新启动连接
                                self._start_connection(live_id)
                        else:
                            # 连接活跃，重置重连计数
                            if conn_info['reconnect_count'] > 0:
                                print(f"【√】直播间 {live_id} 连接已恢复正常")
                                conn_info['reconnect_count'] = 0
                            
                            # 检查是否长时间没有收到消息（可能是静默断开）
                            if current_time - conn_info['last_message_time'] > 60:
                                print(f"【!】直播间 {live_id} 超过60秒未收到消息，可能连接异常")
                                # 可以选择主动断开重连
                                # 但为了避免误判，这里只记录日志
                
            except Exception as e:
                print(f"【X】连接监控线程异常: {e}")
                import traceback
                traceback.print_exc()
        
        print("【X】连接监控线程已停止")
    
    def shutdown(self):
        """关闭连接管理器"""
        print("【!】正在关闭连接管理器...")
        self.running = False
        
        with self.lock:
            for live_id in list(self.connections.keys()):
                self.remove_connection(live_id)
        
        print("【√】连接管理器已关闭")


# 全局单例
_connection_manager = None
_manager_lock = threading.Lock()


def get_connection_manager():
    """
    获取全局连接管理器实例（单例模式）
    
    Returns:
        PersistentConnectionManager: 连接管理器实例
    """
    global _connection_manager
    
    if _connection_manager is None:
        with _manager_lock:
            if _connection_manager is None:
                _connection_manager = PersistentConnectionManager()
    
    return _connection_manager