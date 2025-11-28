#!/usr/bin/python
# coding:utf-8

"""
直播间监听器 - 扩展DouyinLiveWebFetcher并添加消息队列支持
"""

import os
import time
from .liveMan import DouyinLiveWebFetcher
from .protobuf.douyin import (
    ChatMessage, GiftMessage, LikeMessage,
    MemberMessage, SocialMessage, RoomUserSeqMessage,
    FansclubMessage, ControlMessage
)
from ..gift_mapping import get_fortune_type_by_gift, is_valid_gift


class LiveRoomMonitor(DouyinLiveWebFetcher):
    """扩展原有类，添加消息队列支持"""
    
    def __init__(self, live_id, message_queue, event_handler=None):
        """
        初始化直播间监听器
        
        Args:
            live_id: 直播间ID
            message_queue: 消息队列
            event_handler: 事件处理器(可选)
        """
        # 使用完整路径
        abogus_file = os.path.join(os.path.dirname(__file__), 'a_bogus.js')
        super().__init__(live_id, abogus_file)
        self.message_queue = message_queue
        self.is_running = True
        self.event_handler = event_handler
    
    def get_room_status_data(self):
        """
        获取直播间状态数据
        
        Returns:
            dict: 包含 room_status 等信息，如果获取失败返回 None
                  room_status: 0 = 正在直播, 2 = 已结束
        """
        try:
            from .liveMan import generateMsToken
            from urllib3.util.url import parse_url
            import requests
            
            msToken = generateMsToken()
            nonce = self.get_ac_nonce()
            if not nonce:
                raise Exception("无法获取 ac_nonce")
            
            signature = self.get_ac_signature(nonce)
            url = ('https://live.douyin.com/webcast/room/web/enter/?aid=6383'
                   '&app_name=douyin_web&live_id=1&device_platform=web&language=zh-CN&enter_from=page_refresh'
                   '&cookie_enabled=true&screen_width=5120&screen_height=1440&browser_language=zh-CN&browser_platform=Win32'
                   '&browser_name=Edge&browser_version=140.0.0.0'
                   f'&web_rid={self.live_id}'
                   f'&room_id_str={self.room_id}'
                   '&enter_source=&is_need_double_stream=false&insert_task_id=&live_reason=&msToken=' + msToken)
            
            query = parse_url(url).query
            if not query:
                raise Exception("URL query 为空")
            
            params = {i[0]: i[1] for i in [j.split('=') for j in query.split('&')]}
            a_bogus = self.get_a_bogus(params)
            url += f"&a_bogus={a_bogus}"
            
            headers = self.headers.copy()
            headers.update({
                'Referer': f'https://live.douyin.com/{self.live_id}',
                'Cookie': f'ttwid={self.ttwid};__ac_nonce={nonce}; __ac_signature={signature}',
            })
            
            session = requests.Session()
            resp = session.get(url, headers=headers, timeout=10)
            data = resp.json().get('data')
            
            if data:
                room_status = data.get('room_status')
                user = data.get('user')
                user_id = user.get('id_str') if user else 'unknown'
                nickname = user.get('nickname') if user else 'unknown'
                status_text = ['正在直播', '未知状态', '已结束'][room_status] if room_status in [0, 2] else f'未知状态({room_status})'
                print(f"【{nickname}】[{user_id}]直播间状态：{status_text}")
                return data
            else:
                print("【X】无法获取直播间数据")
                return None
                
        except Exception as e:
            print(f"【X】获取直播间状态失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _parseChatMsg(self, payload):
        """聊天消息"""
        try:
            message = ChatMessage().parse(payload)
            # 提取头像URL
            avatar_url = ''
            try:
                if message.user.avatar_thumb and message.user.avatar_thumb.url_list_list:
                    avatar_url = message.user.avatar_thumb.url_list_list[0]
            except:
                pass
            
            data = {
                'type': 'chat',
                'user_id': message.user.id,
                'user_name': message.user.nick_name,
                'content': message.content,
                'user_avatar': avatar_url,
                'timestamp': time.time()
            }
            self.message_queue.put(data)
            
            # 安全打印，避免emoji编码错误
            try:
                print(f"【聊天msg】[{data['user_id']}]{data['user_name']}: {data['content']}")
            except:
                print(f"【聊天msg】[{data['user_id']}]{data['user_name']}: [包含特殊字符]")
            
            # 使用事件处理器处理聊天事件
            if self.event_handler:
                self.event_handler.process_event('chat', data)
        except Exception as e:
            print(f"【X】解析聊天消息失败: {e}")
    
    def _parseGiftMsg(self, payload):
        """礼物消息"""
        message = GiftMessage().parse(payload)
        # 提取头像URL
        avatar_url = ''
        try:
            if message.user.avatar_thumb and message.user.avatar_thumb.url_list_list:
                avatar_url = message.user.avatar_thumb.url_list_list[0]
        except:
            pass
        
        gift_name = message.gift.name
        fortune_type = get_fortune_type_by_gift(gift_name)
        
        data = {
            'type': 'gift',
            'user_id': message.user.id,
            'user_name': message.user.nick_name,
            'gift_name': gift_name,
            'gift_count': message.combo_count,
            'user_avatar': avatar_url,
            'fortune_type': fortune_type,  # 添加运势类型
            'is_valid_gift': is_valid_gift(gift_name),  # 是否是有效礼物
            'timestamp': time.time()
        }
        self.message_queue.put(data)
        
        if fortune_type:
            print(f"【礼物msg】{data['user_name']} 送出了 {gift_name}x{data['gift_count']} -> {fortune_type}运势")
        else:
            print(f"【礼物msg】{data['user_name']} 送出了 {gift_name}x{data['gift_count']}")
        
        # 使用事件处理器处理礼物事件
        if self.event_handler:
            self.event_handler.process_event('gift', data)
    
    def _parseLikeMsg(self, payload):
        """点赞消息"""
        try:
            message = LikeMessage().parse(payload)
            # 提取头像URL
            avatar_url = ''
            try:
                if message.user.avatar_thumb and message.user.avatar_thumb.url_list_list:
                    avatar_url = message.user.avatar_thumb.url_list_list[0]
            except:
                pass
            
            data = {
                'type': 'like',
                'user_id': message.user.id,
                'user_name': message.user.nick_name,
                'count': message.count,
                'user_avatar': avatar_url,
                'timestamp': time.time()
            }
            self.message_queue.put(data)
            
            # 安全打印
            try:
                print(f"【点赞msg】{data['user_name']} 点了{data['count']}个赞")
            except:
                print(f"【点赞msg】[用户名包含特殊字符] 点了{data['count']}个赞")
            
            # 使用事件处理器处理点赞事件
            if self.event_handler:
                self.event_handler.process_event('like', data)
        except Exception as e:
            print(f"【X】解析点赞消息失败: {e}")
    
    def _parseMemberMsg(self, payload):
        """进入直播间消息"""
        try:
            message = MemberMessage().parse(payload)
            # 安全获取性别，如果获取失败则显示"未知"
            try:
                gender = ["女", "男"][message.user.gender] if message.user.gender in [0, 1] else "未知"
            except:
                gender = "未知"
            
            # 提取头像URL
            avatar_url = ''
            try:
                if message.user.avatar_thumb and message.user.avatar_thumb.url_list_list:
                    avatar_url = message.user.avatar_thumb.url_list_list[0]
            except:
                pass
            
            data = {
                'type': 'member',
                'user_id': message.user.id,
                'user_name': message.user.nick_name,
                'gender': gender,
                'user_avatar': avatar_url,
                'timestamp': time.time()
            }
            self.message_queue.put(data)
            
            # 安全打印
            try:
                print(f"【进场msg】[{data['user_id']}][{data['gender']}]{data['user_name']} 进入了直播间")
            except:
                print(f"【进场msg】[{data['user_id']}][{data['gender']}][用户名包含特殊字符] 进入了直播间")
            
            # 使用事件处理器处理进场事件
            if self.event_handler:
                self.event_handler.process_event('member', data)
        except Exception as e:
            print(f"【X】解析进场消息失败: {e}")
    
    def _parseSocialMsg(self, payload):
        """关注消息"""
        message = SocialMessage().parse(payload)
        # 提取头像URL
        avatar_url = ''
        try:
            if message.user.avatar_thumb and message.user.avatar_thumb.url_list_list:
                avatar_url = message.user.avatar_thumb.url_list_list[0]
        except:
            pass
        
        data = {
            'type': 'follow',
            'user_id': message.user.id,
            'user_name': message.user.nick_name,
            'user_avatar': avatar_url,
            'timestamp': time.time()
        }
        self.message_queue.put(data)
        print(f"【关注msg】[{data['user_id']}]{data['user_name']} 关注了主播")
        
        # 使用事件处理器处理关注事件
        if self.event_handler:
            self.event_handler.process_event('follow', data)
    
    def _parseRoomUserSeqMsg(self, payload):
        """直播间统计"""
        message = RoomUserSeqMessage().parse(payload)
        data = {
            'type': 'stats',
            'current_viewers': message.total,
            'total_viewers': message.total_pv_for_anchor,
            'timestamp': time.time()
        }
        self.message_queue.put(data)
        print(f"【统计msg】当前观看人数: {data['current_viewers']}, 累计观看人数: {data['total_viewers']}")
    
    def _parseFansclubMsg(self, payload):
        """粉丝团消息"""
        message = FansclubMessage().parse(payload)
        data = {
            'type': 'fansclub',
            'content': message.content,
            'timestamp': time.time()
        }
        self.message_queue.put(data)
        print(f"【粉丝团msg】 {data['content']}")
    
    def _parseControlMsg(self, payload):
        """直播间状态消息"""
        message = ControlMessage().parse(payload)
        
        if message.status == 3:
            data = {
                'type': 'control',
                'status': 'ended',
                'timestamp': time.time()
            }
            self.message_queue.put(data)
            print("直播间已结束")
            self.stop()