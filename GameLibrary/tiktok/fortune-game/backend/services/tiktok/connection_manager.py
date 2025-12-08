#!/usr/bin/python
# coding:utf-8

"""
持久化连接管理器 - 管理TikTok直播间的持久连接
"""

import threading
import time
import queue
# 使用 Node.js 版本的 LiveRoomMonitor，绕过 Python TikTokLive 库的限制
from .live_monitor_nodejs import LiveRoomMonitor


class PersistentConnectionManager:
    """持久化连接管理器 - 保持TikTok直播间连接始终活跃"""

    def __init__(self):
        """初始化连接管理器"""
        self.connections = {}  # {live_id: ConnectionInfo}
        self.lock = threading.Lock()
        self.running = True

        # 启动监控线程
        self.monitor_thread = threading.Thread(target=self._monitor_connections, daemon=True)
        self.monitor_thread.start()
        print("【√】TikTok持久化连接管理器已启动")

    def add_connection(self, live_id, message_queue):
        """
        添加或恢复一个TikTok直播间连接

        Args:
            live_id: TikTok用户名 (unique_id)
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
                    print(f"【√】TikTok直播间 {live_id} 连接已存在且活跃")
                    return True
                else:
                    print(f"【!】TikTok直播间 {live_id} 连接存在但不活跃，将重新连接")

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
                print(f"【X】添加TikTok连接失败: {e}")
                if live_id in self.connections:
                    del self.connections[live_id]
                raise  # 重新抛出异常，让上层处理

    def remove_connection(self, live_id):
        """
        移除一个TikTok直播间连接

        Args:
            live_id: TikTok用户名
        """
        live_id = str(live_id)

        with self.lock:
            if live_id not in self.connections:
                print(f"【!】TikTok直播间 {live_id} 连接不存在")
                return

            conn_info = self.connections[live_id]

            # 标记不再重连
            conn_info['should_reconnect'] = False

            # 停止监听器
            if conn_info['monitor']:
                try:
                    conn_info['monitor'].stop()
                    print(f"【√】已停止TikTok直播间 {live_id} 的监听器")
                except Exception as e:
                    print(f"【!】停止监听器时出错: {e}")

            # 移除连接
            del self.connections[live_id]
            print(f"【√】已移除TikTok直播间 {live_id} 的连接")

    def get_connection_status(self, live_id):
        """
        获取连接状态

        Args:
            live_id: TikTok用户名

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
            live_id: TikTok用户名
        """
        live_id = str(live_id)

        with self.lock:
            if live_id in self.connections:
                self.connections[live_id]['last_message_time'] = time.time()

    def _start_connection(self, live_id):
        """
        启动一个连接（内部方法，需要在lock内调用）

        Args:
            live_id: TikTok用户名
        """
        if live_id not in self.connections:
            return

        conn_info = self.connections[live_id]

        try:
            # 创建TikTok监听器
            monitor = LiveRoomMonitor(
                live_id,
                conn_info['message_queue']
            )

            conn_info['monitor'] = monitor

            # TikTokLive会在连接时自动检查直播状态
            print(f"【√】准备连接TikTok直播间: {live_id}")

            # 启动监听线程
            def run_monitor():
                try:
                    print(f"【√】开始连接TikTok直播间 {live_id}")
                    conn_info['active'] = True
                    monitor.start()
                except Exception as e:
                    print(f"【X】TikTok直播间 {live_id} 连接异常: {e}")
                    import traceback
                    traceback.print_exc()
                finally:
                    conn_info['active'] = False
                    print(f"【!】TikTok直播间 {live_id} 连接已断开")

            thread = threading.Thread(target=run_monitor, daemon=True)
            thread.start()
            conn_info['thread'] = thread

            print(f"【√】TikTok直播间 {live_id} 连接线程已启动")

        except Exception as e:
            print(f"【X】启动TikTok直播间 {live_id} 连接失败: {e}")
            import traceback
            traceback.print_exc()
            conn_info['active'] = False
            raise

    def _monitor_connections(self):
        """
        监控所有连接的健康状态，自动重连断开的连接
        """
        print("【√】TikTok连接监控线程已启动")

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
                            # 计算重连延迟（指数退避，最大300秒=5分钟）
                            # 避免因速率限制而过快重试
                            reconnect_delay = min(2 ** conn_info['reconnect_count'] * 5, 300)

                            if current_time - conn_info['last_reconnect_time'] >= reconnect_delay:
                                # 限制最大重连次数，避免无限重试
                                if conn_info['reconnect_count'] >= 10:
                                    print(f"【!】TikTok直播间 {live_id} 已达到最大重连次数，暂停重连")
                                    conn_info['should_reconnect'] = False
                                    continue

                                print(f"【!】检测到TikTok直播间 {live_id} 连接断开，等待 {reconnect_delay} 秒后重连（第 {conn_info['reconnect_count'] + 1} 次）")

                                conn_info['reconnect_count'] += 1
                                conn_info['last_reconnect_time'] = current_time

                                # 重新启动连接
                                try:
                                    self._start_connection(live_id)
                                except Exception as e:
                                    error_msg = str(e)
                                    print(f"【X】重连失败: {e}")
                                    # 如果是速率限制错误，增加额外延迟
                                    if 'RATE_LIMIT' in error_msg or 'rate_limit' in error_msg:
                                        print(f"【!】检测到速率限制，将等待更长时间后重试")
                                        conn_info['reconnect_count'] += 2  # 额外增加延迟
                        else:
                            # 连接活跃，重置重连计数
                            if conn_info['reconnect_count'] > 0:
                                print(f"【√】TikTok直播间 {live_id} 连接已恢复正常")
                                conn_info['reconnect_count'] = 0

                            # 检查是否长时间没有收到消息（可能是静默断开）
                            if current_time - conn_info['last_message_time'] > 120:
                                print(f"【!】TikTok直播间 {live_id} 超过120秒未收到消息，可能连接异常")

            except Exception as e:
                print(f"【X】TikTok连接监控线程异常: {e}")
                import traceback
                traceback.print_exc()

        print("【X】TikTok连接监控线程已停止")

    def shutdown(self):
        """关闭连接管理器"""
        print("【!】正在关闭TikTok连接管理器...")
        self.running = False

        with self.lock:
            for live_id in list(self.connections.keys()):
                self.remove_connection(live_id)

        print("【√】TikTok连接管理器已关闭")


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
