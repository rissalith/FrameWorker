#!/usr/bin/python
# coding:utf-8

"""
TikTok直播间监听器 - 使用TikTokLive库
"""

import os
import re
import json
import time
import threading
import asyncio
import httpx
from TikTokLive import TikTokLiveClient
from TikTokLive.events import (
    CommentEvent, GiftEvent, LikeEvent, JoinEvent,
    FollowEvent, ShareEvent, UserStatsEvent,
    ConnectEvent, DisconnectEvent
)
from ..gift_mapping import get_fortune_type_by_gift, is_valid_gift

# 代理配置 - 本地开发使用7897端口，Docker容器内不使用代理
def get_proxy_url():
    """获取代理URL，根据运行环境自动判断"""
    # 检查是否在Docker容器中运行
    is_docker = os.path.exists('/.dockerenv')

    if is_docker:
        # Docker容器内（香港服务器）不需要代理
        return ''

    # 优先使用环境变量配置的代理
    env_proxy = os.environ.get('TIKTOK_PROXY', os.environ.get('HTTPS_PROXY', os.environ.get('HTTP_PROXY', '')))
    if env_proxy:
        return env_proxy

    # 本地开发环境默认使用7897端口代理
    return 'http://127.0.0.1:7897'

PROXY_URL = get_proxy_url()

# 设置环境变量，让 Sign API 的 httpx 客户端也能使用代理
if PROXY_URL:
    os.environ['HTTPS_PROXY'] = PROXY_URL
    os.environ['HTTP_PROXY'] = PROXY_URL
    print(f"【√】TikTok代理已配置: {PROXY_URL}")
    print(f"【√】已设置 HTTPS_PROXY 环境变量: {PROXY_URL}")
else:
    print("【!】TikTok代理未配置，直接连接（适用于海外服务器）")


async def fetch_room_id_from_html(unique_id: str, proxy_url: str = None) -> int:
    """
    通过解析TikTok直播页面HTML获取room_id
    这个方法不需要Sign API的Pro计划，可以绕过付费限制

    Args:
        unique_id: TikTok用户名
        proxy_url: 代理URL（可选）

    Returns:
        int: 直播间的room_id

    Raises:
        Exception: 如果用户不存在、未在直播或被TikTok拦截
    """
    # 正则表达式匹配 SIGI_STATE
    sigi_pattern = re.compile(r'<script id="SIGI_STATE" type="application/json">(.*?)</script>')

    # 创建 httpx 客户端
    client_kwargs = {'timeout': 30.0}
    if proxy_url:
        client_kwargs['proxy'] = proxy_url

    async with httpx.AsyncClient(**client_kwargs) as client:
        # 访问直播页面
        url = f"https://www.tiktok.com/@{unique_id}/live"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        }

        print(f"【√】正在获取 {unique_id} 的 room_id...")
        response = await client.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"访问TikTok页面失败: HTTP {response.status_code}")

        # 解析 SIGI_STATE
        match = sigi_pattern.search(response.text)
        if not match:
            raise Exception("无法解析SIGI_STATE，可能被TikTok拦截（需要人机验证）")

        try:
            sigi_state = json.loads(match.group(1))
        except json.JSONDecodeError:
            raise Exception("SIGI_STATE JSON解析失败")

        # 检查 LiveRoom 数据
        if sigi_state.get('LiveRoom') is None:
            raise Exception(f"用户 {unique_id} 从未直播过或不存在")

        # 获取 room_id 和状态
        room_data = sigi_state["LiveRoom"]["liveRoomUserInfo"]["user"]
        room_id = room_data.get('roomId')
        status = room_data.get('status')

        if not room_id:
            raise Exception(f"无法获取 {unique_id} 的 room_id")

        # status: 2 = 正在直播, 4 = 离线
        if status == 4:
            print(f"【!】用户 {unique_id} 当前未在直播 (status={status})")
        else:
            print(f"【√】获取到 room_id: {room_id} (status={status})")

        return int(room_id)


def safe_get_user_data(event, use_user_info=True):
    """
    安全获取用户数据，处理TikTokLive库的属性访问bug

    Args:
        event: TikTokLive事件对象
        use_user_info: 是否尝试使用user_info属性（CommentEvent等有此属性）

    Returns:
        dict: 包含 user_id, nickname, avatar_url 的字典
    """
    user_id = 'unknown'
    nickname = 'Unknown User'
    avatar_url = ''

    try:
        # 尝试使用 user_info（某些事件有这个属性）
        if use_user_info and hasattr(event, 'user_info'):
            user_info = event.user_info
            if hasattr(user_info, 'user_id'):
                user_id = str(user_info.user_id)
            if hasattr(user_info, 'nick_name'):
                nickname = user_info.nick_name
            elif hasattr(user_info, 'nickname'):
                nickname = user_info.nickname
            # 获取头像
            if hasattr(user_info, 'avatar_thumb') and user_info.avatar_thumb:
                if hasattr(user_info.avatar_thumb, 'urls') and user_info.avatar_thumb.urls:
                    avatar_url = user_info.avatar_thumb.urls[0]
    except Exception as e:
        pass  # 静默处理错误

    # 如果上面的方法失败，尝试直接从 to_pydict() 获取
    if user_id == 'unknown':
        try:
            data = event.to_pydict()
            if 'userInfo' in data:
                ui = data['userInfo']
                user_id = str(ui.get('userId', ui.get('user_id', 'unknown')))
                nickname = ui.get('nickName', ui.get('nick_name', 'Unknown User'))
                if 'avatarThumb' in ui:
                    at = ui['avatarThumb']
                    if isinstance(at, dict) and 'urls' in at and at['urls']:
                        avatar_url = at['urls'][0]
            elif 'user' in data:
                u = data['user']
                user_id = str(u.get('userId', u.get('user_id', 'unknown')))
                nickname = u.get('nickName', u.get('nick_name', 'Unknown User'))
                if 'avatarThumb' in u:
                    at = u['avatarThumb']
                    if isinstance(at, dict) and 'urls' in at and at['urls']:
                        avatar_url = at['urls'][0]
        except Exception as e:
            pass  # 静默处理错误

    return {
        'user_id': user_id,
        'nickname': nickname,
        'avatar_url': avatar_url
    }


class LiveRoomMonitor:
    """TikTok直播间监听器"""

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
            live_id: TikTok用户名 (unique_id)
            message_queue: 消息队列
            event_handler: 事件处理器(可选)
        """
        self.live_id = live_id
        self.message_queue = message_queue
        self.event_handler = event_handler
        self.is_running = False
        self.client = None
        self._loop = None
        self._thread = None

        print(f"【√】TikTok直播间监听器已创建: {live_id}")

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
        TikTok API不支持直接查询状态，返回模拟数据

        Returns:
            dict: 包含 room_status 等信息
        """
        # TikTokLive库会在连接时自动检查直播状态
        # 这里返回默认的正在直播状态
        return {
            'room_status': 0,  # 0 = 正在直播
            'user': {
                'id_str': self.live_id,
                'nickname': self.live_id
            }
        }

    def _setup_client(self):
        """设置TikTok客户端和事件处理器"""
        # 配置代理 - 动态创建代理对象（必须在当前事件循环中创建）
        # TikTokLive v6.6.5 参数:
        #   - web_proxy: 用于 TikTok API 请求 (httpx，接受 URL 字符串)
        #   - ws_proxy: 用于 WebSocket 连接 (python_socks.async_.asyncio.Proxy 对象)
        # 注意: Sign API 的代理通过 HTTPS_PROXY 环境变量设置（在模块加载时已配置）
        if PROXY_URL:
            try:
                from python_socks.async_.asyncio import Proxy as AsyncioProxy
                # 每次连接时创建新的代理对象，确保它绑定到当前的事件循环
                ws_proxy = AsyncioProxy.from_url(PROXY_URL)
                web_proxy = PROXY_URL

                print(f"【√】使用代理连接TikTok: {PROXY_URL}")
                self.client = TikTokLiveClient(
                    unique_id=self.live_id,
                    web_proxy=web_proxy,
                    ws_proxy=ws_proxy
                )
            except Exception as e:
                print(f"【!】创建代理对象失败: {e}，不使用代理连接")
                self.client = TikTokLiveClient(unique_id=self.live_id)
        else:
            print(f"【!】未配置代理，直接连接TikTok（可能需要VPN）")
            self.client = TikTokLiveClient(unique_id=self.live_id)

        @self.client.on(ConnectEvent)
        async def on_connect(event: ConnectEvent):
            print(f"【√】已连接到TikTok直播间: {self.live_id}")
            self.is_running = True
            data = {
                'type': 'connected',
                'live_id': self.live_id,
                'timestamp': time.time()
            }
            self.message_queue.put(data)

        @self.client.on(DisconnectEvent)
        async def on_disconnect(event: DisconnectEvent):
            print(f"【!】TikTok直播间已断开: {self.live_id}")
            self.is_running = False
            data = {
                'type': 'control',
                'status': 'ended',
                'timestamp': time.time()
            }
            self.message_queue.put(data)

        @self.client.on(CommentEvent)
        async def on_comment(event: CommentEvent):
            """聊天消息"""
            try:
                # 使用安全的方法获取用户数据
                user_data = safe_get_user_data(event)

                data = {
                    'type': 'chat',
                    'user_id': user_data['user_id'],
                    'user_name': user_data['nickname'],
                    'content': event.comment,
                    'user_avatar': user_data['avatar_url'],
                    'timestamp': time.time()
                }
                self.message_queue.put(data)

                try:
                    print(f"【聊天msg】[{data['user_id']}]{data['user_name']}: {data['content']}")
                except:
                    print(f"【聊天msg】[{data['user_id']}]{data['user_name']}: [包含特殊字符]")

                if self.event_handler:
                    self.event_handler.process_event('chat', data)
            except Exception as e:
                print(f"【X】解析聊天消息失败: {e}")

        @self.client.on(GiftEvent)
        async def on_gift(event: GiftEvent):
            """礼物消息"""
            try:
                # 使用安全的方法获取用户数据
                user_data = safe_get_user_data(event)

                # 获取礼物信息
                gift_name = 'Unknown'
                gift_count = 1
                try:
                    gift_name = event.gift.name if hasattr(event, 'gift') and hasattr(event.gift, 'name') else 'Unknown'
                    gift_count = event.gift.count if hasattr(event, 'gift') and hasattr(event.gift, 'count') else 1
                except:
                    try:
                        data = event.to_pydict()
                        if 'gift' in data:
                            gift_name = data['gift'].get('name', 'Unknown')
                            gift_count = data['gift'].get('count', 1)
                    except:
                        pass

                fortune_type = self.get_fortune_type(gift_name)

                data = {
                    'type': 'gift',
                    'user_id': user_data['user_id'],
                    'user_name': user_data['nickname'],
                    'gift_name': gift_name,
                    'gift_count': gift_count,
                    'user_avatar': user_data['avatar_url'],
                    'fortune_type': fortune_type,
                    'is_valid_gift': fortune_type is not None,
                    'timestamp': time.time()
                }
                self.message_queue.put(data)

                if fortune_type:
                    print(f"【礼物msg】{data['user_name']} 送出了 {gift_name}x{data['gift_count']} -> {fortune_type}运势")
                else:
                    print(f"【礼物msg】{data['user_name']} 送出了 {gift_name}x{data['gift_count']}")

                if self.event_handler:
                    self.event_handler.process_event('gift', data)
            except Exception as e:
                print(f"【X】解析礼物消息失败: {e}")

        @self.client.on(LikeEvent)
        async def on_like(event: LikeEvent):
            """点赞消息"""
            try:
                # LikeEvent 没有 user_info，需要用 to_pydict 获取用户数据
                user_data = safe_get_user_data(event, use_user_info=False)

                # 获取点赞数量
                like_count = 1
                try:
                    # 尝试不同的属性名
                    if hasattr(event, 'count'):
                        like_count = event.count
                    elif hasattr(event, 'total'):
                        like_count = event.total
                    elif hasattr(event, 'likes'):
                        like_count = event.likes
                except:
                    pass

                data = {
                    'type': 'like',
                    'user_id': user_data['user_id'],
                    'user_name': user_data['nickname'],
                    'count': like_count,
                    'user_avatar': user_data['avatar_url'],
                    'timestamp': time.time()
                }
                self.message_queue.put(data)

                try:
                    print(f"【点赞msg】{data['user_name']} 点了{data['count']}个赞")
                except:
                    print(f"【点赞msg】[用户名包含特殊字符] 点了{data['count']}个赞")

                if self.event_handler:
                    self.event_handler.process_event('like', data)
            except Exception as e:
                print(f"【X】解析点赞消息失败: {e}")

        @self.client.on(JoinEvent)
        async def on_join(event: JoinEvent):
            """进入直播间消息"""
            try:
                # 使用安全的方法获取用户数据
                user_data = safe_get_user_data(event)

                data = {
                    'type': 'member',
                    'user_id': user_data['user_id'],
                    'user_name': user_data['nickname'],
                    'gender': 'unknown',  # TikTok API 不提供性别信息
                    'user_avatar': user_data['avatar_url'],
                    'timestamp': time.time()
                }
                self.message_queue.put(data)

                try:
                    print(f"【进场msg】[{data['user_id']}]{data['user_name']} 进入了直播间")
                except:
                    print(f"【进场msg】[{data['user_id']}][用户名包含特殊字符] 进入了直播间")

                if self.event_handler:
                    self.event_handler.process_event('member', data)
            except Exception as e:
                print(f"【X】解析进场消息失败: {e}")

        @self.client.on(FollowEvent)
        async def on_follow(event: FollowEvent):
            """关注消息"""
            try:
                # 使用安全的方法获取用户数据
                user_data = safe_get_user_data(event)

                data = {
                    'type': 'follow',
                    'user_id': user_data['user_id'],
                    'user_name': user_data['nickname'],
                    'user_avatar': user_data['avatar_url'],
                    'timestamp': time.time()
                }
                self.message_queue.put(data)
                print(f"【关注msg】[{data['user_id']}]{data['user_name']} 关注了主播")

                if self.event_handler:
                    self.event_handler.process_event('follow', data)
            except Exception as e:
                print(f"【X】解析关注消息失败: {e}")

        @self.client.on(ShareEvent)
        async def on_share(event: ShareEvent):
            """分享消息"""
            try:
                # 使用安全的方法获取用户数据
                user_data = safe_get_user_data(event)

                data = {
                    'type': 'share',
                    'user_id': user_data['user_id'],
                    'user_name': user_data['nickname'],
                    'user_avatar': user_data['avatar_url'],
                    'timestamp': time.time()
                }
                self.message_queue.put(data)
                print(f"【分享msg】[{data['user_id']}]{data['user_name']} 分享了直播间")

                if self.event_handler:
                    self.event_handler.process_event('share', data)
            except Exception as e:
                print(f"【X】解析分享消息失败: {e}")

        @self.client.on(UserStatsEvent)
        async def on_user_stats(event: UserStatsEvent):
            """观众数量更新"""
            try:
                data = {
                    'type': 'stats',
                    'current_viewers': event.viewer_count if hasattr(event, 'viewer_count') else 0,
                    'total_viewers': event.total_viewer_count if hasattr(event, 'total_viewer_count') else 0,
                    'timestamp': time.time()
                }
                self.message_queue.put(data)
                print(f"【统计msg】当前观看人数: {data['current_viewers']}")
            except Exception as e:
                print(f"【X】解析统计消息失败: {e}")

    def _run_client(self):
        """在新线程中运行异步客户端"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            # 第一步：先获取 room_id（绕过 Sign API Pro 计划限制）
            # 通过解析 HTML 页面获取 room_id，不需要 Sign API
            print(f"【√】正在连接TikTok用户: {self.live_id}")
            room_id = self._loop.run_until_complete(
                fetch_room_id_from_html(self.live_id, PROXY_URL)
            )

            # 第二步：设置客户端并使用 room_id 连接
            self._setup_client()
            # 传入 room_id 可以跳过 Sign API 的 unique_id 查询限制
            # fetch_live_check=False 跳过直播状态检查（因为我们已经知道 room_id）
            # 使用 connect() 而不是 start()，connect() 会阻塞直到连接断开
            # start() 是非阻塞的，返回 Task 后立即退出
            self._loop.run_until_complete(
                self.client.connect(room_id=room_id, fetch_live_check=False)
            )
        except Exception as e:
            error_msg = str(e)
            print(f"【X】TikTok客户端运行异常: {error_msg}")

            # 提供更有帮助的错误信息
            if "ConnectTimeout" in error_msg or "timeout" in error_msg.lower():
                print("【提示】连接超时，可能原因:")
                print("  1. 需要VPN或代理才能访问TikTok")
                print("  2. 设置环境变量 TIKTOK_PROXY=http://代理地址:端口")
            elif "MissingRoomId" in error_msg or "nonexistent" in error_msg.lower():
                print("【提示】无法找到直播间，可能原因:")
                print("  1. 用户名输入错误")
                print("  2. 该用户当前没有在直播")
                print("  3. 被TikTok检测到请求异常")
            elif "402" in error_msg or "Pro plan" in error_msg:
                print("【提示】Sign API 返回 402 错误")
                print("  这通常是因为 room_id 获取失败，请检查网络连接")

            import traceback
            traceback.print_exc()
        finally:
            self.is_running = False
            self._loop.close()

    def start(self):
        """启动监听"""
        if self.is_running:
            print(f"【!】监听器已在运行中")
            return

        print(f"【√】启动TikTok直播间监听: {self.live_id}")
        self._run_client()

    def stop(self):
        """停止监听"""
        print(f"【√】停止TikTok直播间监听: {self.live_id}")
        self.is_running = False

        if self.client:
            try:
                if self._loop and self._loop.is_running():
                    asyncio.run_coroutine_threadsafe(self.client.stop(), self._loop)
                else:
                    # 如果loop不在运行，创建新的来停止
                    asyncio.run(self.client.stop())
            except Exception as e:
                print(f"【!】停止客户端时出错: {e}")
