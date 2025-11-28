#!/usr/bin/python
# coding:utf-8

"""
测试直播间状态检查
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from services.douyin.live_monitor import LiveRoomMonitor
import queue

def test_live_room(live_id):
    """测试单个直播间"""
    print("=" * 80)
    print(f"测试直播间: {live_id}")
    print("=" * 80)
    
    try:
        # 创建监听器
        message_queue = queue.Queue()
        abogus_file = os.path.join(os.path.dirname(__file__), 'services', 'douyin', 'a_bogus.js')
        monitor = LiveRoomMonitor(live_id, message_queue)
        
        # 获取状态
        print(f"\n【1】正在获取直播间状态...")
        status_data = monitor.get_room_status_data()
        
        if status_data:
            room_status = status_data.get('room_status')
            user = status_data.get('user', {})
            nickname = user.get('nickname', 'unknown')
            user_id = user.get('id_str', 'unknown')
            
            print(f"\n【结果】")
            print(f"  主播: {nickname} ({user_id})")
            print(f"  room_status: {room_status}")
            
            if room_status == 0:
                print(f"  状态: ✅ 正在直播")
                return True
            elif room_status == 2:
                print(f"  状态: ❌ 直播已结束/未开播")
                return False
            else:
                print(f"  状态: ⚠️ 未知状态 ({room_status})")
                return False
        else:
            print(f"\n【结果】❌ 无法获取直播间数据")
            return False
            
    except Exception as e:
        print(f"\n【错误】{e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # 测试不在线的直播间
    print("\n\n")
    test_live_room('527378756578')
    
    print("\n\n")
    # 测试在线的直播间
    test_live_room('866404185102')
    
    print("\n\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)