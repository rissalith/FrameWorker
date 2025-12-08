#!/usr/bin/python
# coding:utf-8

"""
TikTok直播间监听器 - 使用Node.js TikTok-Live-Connector库
通过子进程调用Node.js脚本，绕过Python TikTokLive库的限制
"""

import os
import json
import time
import subprocess
import threading
import sys

# 设置 stdout 和 stderr 为无缓冲模式
sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
sys.stderr.reconfigure(line_buffering=True) if hasattr(sys.stderr, 'reconfigure') else None

from ..gift_mapping import get_fortune_type_by_gift

# 获取项目根目录 (巫女上上签)
# __file__ = live_monitor_nodejs.py
# abspath(__file__) = 完整路径，包含文件名
# 路径: c:\巫女上上签\GameLibrary\games\fortune-game-tiktok\backend\services\tiktok\live_monitor_nodejs.py
# 需要7次dirname:
#   1. 去掉文件名 -> tiktok/
#   2. -> services/
#   3. -> backend/
#   4. -> fortune-game-tiktok/
#   5. -> games/
#   6. -> GameLibrary/
#   7. -> 巫女上上签/
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))))

# Node.js 脚本路径
NODEJS_SCRIPT_DIR = os.path.join(PROJECT_ROOT, 'TikTok-Live-Connector-ts-rewrite')
NODEJS_SCRIPT = os.path.join(NODEJS_SCRIPT_DIR, 'main.js')


class LiveRoomMonitor:
    """TikTok直播间监听器 - 基于Node.js子进程"""

    # TikTok礼物名称到运势类型的映射
    TIKTOK_GIFT_MAPPING = {
        # 日常运势 (低价值礼物)
        'Rose': 'daily',
        'TikTok': 'daily',
        'Heart': 'daily',
        'Ice Cream Cone': 'daily',
        'Finger Heart': 'daily',
        'GG': 'daily',
        'Rosa': 'daily',
        'Hi': 'daily',

        # 爱情运势 (爱心相关礼物)
        'Love you': 'love',
        'Hearts': 'love',
        'Heart Me': 'love',
        'Love Bang': 'love',
        'Love': 'love',
        'Paper Crane': 'love',
        'Forever Rosa': 'love',
        'Chasing the Dream': 'love',

        # 财运 (价值中等礼物)
        'Doughnut': 'wealth',
        'Caps': 'wealth',
        'Money Gun': 'wealth',
        'Gold Mine': 'wealth',
        'Hat and Mustache': 'wealth',
        'Lucky Money': 'wealth',
        'CORGI': 'wealth',
        'Little Crown': 'wealth',

        # 事业运 (高价值礼物)
        'Lion': 'career',
        'Drama Queen': 'career',
        'Rock Star': 'career',
        'Super Car': 'career',
        'Rocket': 'career',
        'Trending': 'career',
        'Star': 'career',
        'Crown': 'career',

        # 健康运 (健康/运动相关)
        'Weights': 'health',
        'Massage Chair': 'health',
        'Fruit Friends': 'health',
        'Perfume': 'health',
        'Lucky Airdrop Box': 'health',
        'Gem Gun': 'health',
        'Sunglasses': 'health',
        'Bear Love': 'health',
    }

    def __init__(self, live_id, message_queue, event_handler=None):
        """
        初始化TikTok直播间监听器

        Args:
            live_id: TikTok用户名 (unique_id) 或 room_id
            message_queue: 消息队列
            event_handler: 事件处理器(可选)
        """
        self.live_id = live_id
        self.message_queue = message_queue
        self.event_handler = event_handler
        self.is_running = False
        self._process = None
        self._reader_thread = None
        self._stop_event = threading.Event()

        print(f"【√】TikTok直播间监听器已创建(Node.js): {live_id}", flush=True)

    def get_fortune_type(self, gift_name):
        """
        根据TikTok礼物名获取运势类型

        Args:
            gift_name: 礼物名称

        Returns:
            str: 运势类型 (daily/love/wealth/career/health) 或 None
        """
        # 先尝试精确匹配
        if gift_name in self.TIKTOK_GIFT_MAPPING:
            return self.TIKTOK_GIFT_MAPPING[gift_name]

        # 尝试不区分大小写匹配
        gift_lower = gift_name.lower()
        for name, fortune_type in self.TIKTOK_GIFT_MAPPING.items():
            if name.lower() == gift_lower:
                return fortune_type

        # 尝试使用通用的gift_mapping
        return get_fortune_type_by_gift(gift_name)

    def get_room_status_data(self):
        """
        获取直播间状态数据

        Returns:
            dict: 包含 room_status 等信息
        """
        return {
            'room_status': 0 if self.is_running else 1,
            'user': {
                'id_str': self.live_id,
                'nickname': self.live_id
            }
        }

    def _process_message(self, msg_data):
        """
        处理Node.js脚本输出的JSON消息

        Args:
            msg_data: 解析后的JSON数据
        """
        msg_type = msg_data.get('type')

        if msg_type == 'chat':
            data = {
                'type': 'chat',
                'user_id': msg_data.get('user', 'unknown'),
                'user_name': msg_data.get('nickname', 'Unknown User'),
                'content': msg_data.get('text', ''),
                'user_avatar': '',
                'timestamp': msg_data.get('timestamp', time.time()) / 1000
            }
            self.message_queue.put(data)
            try:
                print(f"【聊天msg】[{data['user_id']}]{data['user_name']}: {data['content']}")
            except:
                print(f"【聊天msg】[{data['user_id']}]{data['user_name']}: [包含特殊字符]")

            if self.event_handler:
                self.event_handler.process_event('chat', data)

        elif msg_type == 'gift':
            gift_name = msg_data.get('gift_name', 'Unknown')
            fortune_type = self.get_fortune_type(gift_name)

            data = {
                'type': 'gift',
                'user_id': msg_data.get('user', 'unknown'),
                'user_name': msg_data.get('nickname', 'Unknown User'),
                'gift_name': gift_name,
                'gift_count': msg_data.get('count', 1),
                'user_avatar': '',
                'fortune_type': fortune_type,
                'is_valid_gift': fortune_type is not None,
                'timestamp': msg_data.get('timestamp', time.time()) / 1000
            }
            self.message_queue.put(data)

            if fortune_type:
                print(f"【礼物msg】{data['user_name']} 送出了 {gift_name}x{data['gift_count']} -> {fortune_type}运势")
            else:
                print(f"【礼物msg】{data['user_name']} 送出了 {gift_name}x{data['gift_count']}")

            if self.event_handler:
                self.event_handler.process_event('gift', data)

        elif msg_type == 'like':
            data = {
                'type': 'like',
                'user_id': msg_data.get('user', 'unknown'),
                'user_name': msg_data.get('nickname', 'Unknown User'),
                'count': msg_data.get('count', 1),
                'total': msg_data.get('total', 0),
                'user_avatar': '',
                'timestamp': msg_data.get('timestamp', time.time()) / 1000
            }
            self.message_queue.put(data)
            try:
                print(f"【点赞msg】{data['user_name']} 点了{data['count']}个赞")
            except:
                print(f"【点赞msg】[用户名包含特殊字符] 点了{data['count']}个赞")

            if self.event_handler:
                self.event_handler.process_event('like', data)

        elif msg_type == 'member':
            data = {
                'type': 'member',
                'user_id': msg_data.get('user', 'unknown'),
                'user_name': msg_data.get('nickname', 'Unknown User'),
                'gender': 'unknown',
                'user_avatar': '',
                'timestamp': msg_data.get('timestamp', time.time()) / 1000
            }
            self.message_queue.put(data)
            try:
                print(f"【进场msg】[{data['user_id']}]{data['user_name']} 进入了直播间")
            except:
                print(f"【进场msg】[{data['user_id']}][用户名包含特殊字符] 进入了直播间")

            if self.event_handler:
                self.event_handler.process_event('member', data)

        elif msg_type == 'follow':
            data = {
                'type': 'follow',
                'user_id': msg_data.get('user', 'unknown'),
                'user_name': msg_data.get('nickname', 'Unknown User'),
                'user_avatar': '',
                'timestamp': msg_data.get('timestamp', time.time()) / 1000
            }
            self.message_queue.put(data)
            print(f"【关注msg】[{data['user_id']}]{data['user_name']} 关注了主播")

            if self.event_handler:
                self.event_handler.process_event('follow', data)

        elif msg_type == 'share':
            data = {
                'type': 'share',
                'user_id': msg_data.get('user', 'unknown'),
                'user_name': msg_data.get('nickname', 'Unknown User'),
                'user_avatar': '',
                'timestamp': msg_data.get('timestamp', time.time()) / 1000
            }
            self.message_queue.put(data)
            print(f"【分享msg】[{data['user_id']}]{data['user_name']} 分享了直播间")

            if self.event_handler:
                self.event_handler.process_event('share', data)

        elif msg_type == 'roomUser':
            data = {
                'type': 'stats',
                'current_viewers': msg_data.get('viewerCount', 0),
                'total_viewers': msg_data.get('viewerCount', 0),
                'timestamp': msg_data.get('timestamp', time.time()) / 1000
            }
            self.message_queue.put(data)
            print(f"【统计msg】当前观看人数: {data['current_viewers']}")

    def _read_output(self):
        """读取Node.js子进程的输出"""
        print(f"【√】开始读取Node.js输出...")

        while not self._stop_event.is_set() and self._process:
            try:
                line = self._process.stdout.readline()
                if not line:
                    if self._process.poll() is not None:
                        print(f"【!】Node.js进程已退出，退出码: {self._process.returncode}")
                        break
                    continue

                line = line.strip()
                if not line:
                    continue

                # 尝试解析JSON
                try:
                    msg_data = json.loads(line)
                    self._process_message(msg_data)
                except json.JSONDecodeError:
                    # 不是JSON，可能是普通日志
                    print(f"【Node.js】{line}")

            except Exception as e:
                if not self._stop_event.is_set():
                    print(f"【X】读取Node.js输出错误: {e}")
                break

        self.is_running = False
        print(f"【!】Node.js输出读取线程已退出")

        # 发送断开连接消息
        data = {
            'type': 'control',
            'status': 'ended',
            'timestamp': time.time()
        }
        self.message_queue.put(data)

    def _read_stderr(self):
        """读取Node.js子进程的stderr输出"""
        while not self._stop_event.is_set() and self._process:
            try:
                line = self._process.stderr.readline()
                if not line:
                    if self._process.poll() is not None:
                        break
                    continue

                line = line.strip()
                if line:
                    print(f"【Node.js系统】{line}")

            except Exception as e:
                if not self._stop_event.is_set():
                    print(f"【X】读取Node.js stderr错误: {e}")
                break

    def start(self):
        """启动监听"""
        if self.is_running:
            print(f"【!】监听器已在运行中")
            return

        # 检查Node.js脚本是否存在
        if not os.path.exists(NODEJS_SCRIPT):
            raise Exception(f"Node.js脚本不存在: {NODEJS_SCRIPT}")

        print(f"【√】启动TikTok直播间监听(Node.js): {self.live_id}")
        print(f"【√】脚本路径: {NODEJS_SCRIPT}")

        # 构建命令
        # 检测是否是room_id（纯数字）还是用户名
        if self.live_id.isdigit():
            cmd = ['node', NODEJS_SCRIPT, '--room', self.live_id]
        else:
            cmd = ['node', NODEJS_SCRIPT, self.live_id]

        print(f"【√】执行命令: {' '.join(cmd)}")

        try:
            # 启动Node.js子进程
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                cwd=NODEJS_SCRIPT_DIR,
                encoding='utf-8',
                errors='replace'
            )

            self.is_running = True
            self._stop_event.clear()

            # 发送连接成功消息
            data = {
                'type': 'connected',
                'live_id': self.live_id,
                'timestamp': time.time()
            }
            self.message_queue.put(data)

            # 启动输出读取线程
            self._reader_thread = threading.Thread(target=self._read_output, daemon=True)
            self._reader_thread.start()

            # 启动stderr读取线程
            self._stderr_thread = threading.Thread(target=self._read_stderr, daemon=True)
            self._stderr_thread.start()

            print(f"【√】Node.js进程已启动，PID: {self._process.pid}")

            # 等待进程结束
            self._process.wait()

        except Exception as e:
            print(f"【X】启动Node.js进程失败: {e}")
            import traceback
            traceback.print_exc()
            self.is_running = False
            raise

    def stop(self):
        """停止监听"""
        print(f"【√】停止TikTok直播间监听(Node.js): {self.live_id}")

        self._stop_event.set()
        self.is_running = False

        if self._process:
            try:
                self._process.terminate()
                # 等待进程结束
                try:
                    self._process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"【!】Node.js进程未响应，强制终止")
                    self._process.kill()
            except Exception as e:
                print(f"【!】停止Node.js进程时出错: {e}")
            finally:
                self._process = None

        print(f"【√】Node.js监听器已停止")
