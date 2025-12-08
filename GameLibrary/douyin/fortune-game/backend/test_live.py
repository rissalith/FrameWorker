#!/usr/bin/python
# coding:utf-8

"""
测试抖音直播监听功能
"""

import sys
import time
from services.douyin.live_monitor import LiveRoomMonitor
import queue

def test_live_monitor(live_id):
    """
    测试直播间监听
    
    Args:
        live_id: 直播间ID
    """
    print("=" * 60)
    print(f"开始测试直播间监听: {live_id}")
    print("=" * 60)
    
    # 创建消息队列
    message_queue = queue.Queue()
    
    # 创建监听器
    try:
        monitor = LiveRoomMonitor(live_id, message_queue)
        print("[OK] 监听器创建成功")
        print(f"  - Live ID: {monitor.live_id}")
        print(f"  - Room ID: {monitor.room_id}")
        print(f"  - TTWID: {monitor.ttwid}")
        print("=" * 60)
        
        # 启动监听
        print("开始监听直播间消息...")
        print("按 Ctrl+C 停止监听")
        print("=" * 60)
        
        # 在单独的线程中启动监听
        import threading
        monitor_thread = threading.Thread(target=monitor.start, daemon=True)
        monitor_thread.start()
        
        # 主线程处理消息队列
        message_count = 0
        while True:
            try:
                # 从队列获取消息
                msg = message_queue.get(timeout=1)
                message_count += 1
                
                # 输出JSON格式的消息供Node.js解析
                import json
                try:
                    # 使用ensure_ascii=True避免Windows GBK编码问题
                    json_str = json.dumps(msg, ensure_ascii=True)
                    print(json_str)
                    sys.stdout.flush()  # 立即刷新输出
                except Exception as e:
                    # 如果JSON序列化失败,记录错误但继续运行
                    print(f'{{"type":"error","message":"JSON序列化失败: {str(e)}"}}', file=sys.stderr)
                
            except queue.Empty:
                continue
            except KeyboardInterrupt:
                print("\n\n停止监听...", file=sys.stderr)
                monitor.stop()
                break
                
    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("=" * 60)
    print(f"测试完成! 共接收到 {message_count} 条消息")
    print("=" * 60)
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("使用方法: python test_live.py <直播间ID>")
        print("示例: python test_live.py 261378947940")
        sys.exit(1)
    
    live_id = sys.argv[1]
    test_live_monitor(live_id)