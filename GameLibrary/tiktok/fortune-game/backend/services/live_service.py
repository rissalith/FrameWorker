#!/usr/bin/python
# coding:utf-8

"""
TikTok直播服务层 - 处理TikTok直播间相关业务逻辑
"""

import threading
import queue
import time
from .tiktok.live_monitor import LiveRoomMonitor
from .tiktok.connection_manager import get_connection_manager


class LiveService:
    """直播服务 - 管理直播间连接和消息处理"""
    
    def __init__(self, socketio):
        """
        初始化直播服务
        
        Args:
            socketio: SocketIO实例
        """
        self.socketio = socketio
        self.message_queues = {}  # 存储消息队列
        self.connection_manager = get_connection_manager()  # 使用持久化连接管理器
        print("【√】LiveService已初始化，使用持久化连接管理器")
    
    def start_live(self, live_id):
        """
        开始监听直播间
        
        Args:
            live_id: 直播间ID
            
        Returns:
            dict: 包含success和message的结果
        """
        # 统一转换为字符串类型
        live_id = str(live_id)
        
        # 检查连接状态
        status = self.connection_manager.get_connection_status(live_id)
        if status.get('exists') and status.get('active'):
            print(f"【√】直播间 {live_id} 已在监听中")
            return {
                'success': True,
                'message': f'直播间 {live_id} 已在监听中',
                'live_id': live_id
            }
        
        try:
            print(f"【√】开始启动直播间监听: {live_id}")
            
            # 创建或获取消息队列
            if live_id not in self.message_queues:
                self.message_queues[live_id] = queue.Queue()
                print(f"【√】消息队列已创建")
                
                # 启动消息发送线程
                sender_thread = threading.Thread(
                    target=self._message_sender,
                    args=(live_id,),
                    daemon=True
                )
                sender_thread.start()
                print(f"【√】消息发送线程已启动")
            
            # 使用持久化连接管理器添加连接
            success = self.connection_manager.add_connection(
                live_id,
                self.message_queues[live_id]
            )
            
            if success:
                print(f"【√】直播间 {live_id} 已添加到持久化连接管理器")
                return {
                    'success': True,
                    'message': f'成功开始监听直播间 {live_id}',
                    'live_id': live_id
                }
            else:
                raise Exception("添加到连接管理器失败")
                
        except Exception as e:
            print(f"【X】启动直播间监听失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 清理资源
            if live_id in self.message_queues:
                del self.message_queues[live_id]
            
            return {
                'success': False,
                'message': f'启动失败: {str(e)}'
            }
    
    def stop_live(self, live_id):
        """
        停止监听直播间
        
        Args:
            live_id: 直播间ID
            
        Returns:
            dict: 包含success和message的结果
        """
        # 统一转换为字符串类型
        live_id = str(live_id)
        
        try:
            # 从连接管理器中移除连接
            self.connection_manager.remove_connection(live_id)
            
            # 清理消息队列
            if live_id in self.message_queues:
                del self.message_queues[live_id]
                print(f"【√】已清理直播间 {live_id} 的消息队列")
            
            return {
                'success': True,
                'message': f'已停止监听直播间 {live_id}'
            }
        except Exception as e:
            print(f"【X】停止直播间 {live_id} 时发生错误: {e}")
            # 即使出错也清理资源
            if live_id in self.message_queues:
                del self.message_queues[live_id]
            return {
                'success': False,
                'message': f'停止失败: {str(e)}'
            }
    
    def get_status(self):
        """
        获取当前监听状态
        
        Returns:
            dict: 包含活跃直播间列表和数量
        """
        connections = self.connection_manager.get_all_connections()
        return {
            'success': True,
            'active_rooms': list(connections.keys()),
            'count': len(connections),
            'connections': connections  # 包含详细的连接状态
        }
    
    def _message_sender(self, live_id):
        """
        从队列中读取消息并通过WebSocket发送
        
        Args:
            live_id: 直播间ID
        """
        print(f"【√】消息发送线程已启动，直播间ID: {live_id}")
        print(f"【调试】消息队列对象: {self.message_queues.get(live_id)}")
        
        while live_id in self.message_queues:
            try:
                msg = self.message_queues[live_id].get(timeout=1)
                
                # 更新连接管理器的最后消息时间
                self.connection_manager.update_message_time(live_id)
                
                # 添加live_id到消息中,方便前端识别来源
                msg['live_id'] = live_id
                print(f"【→】发送消息到前端: {msg['type']} - {msg}")
                self.socketio.emit('live_message', msg, room=live_id)
                print(f"【√】消息已通过SocketIO发送")
            except queue.Empty:
                # 每秒检查一次队列
                continue
            except Exception as e:
                print(f"【X】发送消息错误: {e}")
                import traceback
                traceback.print_exc()
                break
        print(f"【X】消息发送线程已停止，直播间ID: {live_id}")