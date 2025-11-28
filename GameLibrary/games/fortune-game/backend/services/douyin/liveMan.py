#!/usr/bin/python
# coding:utf-8

# @FileName:    liveMan.py
# @Time:        2024/1/2 21:51
# @Author:      bubu
# @Project:     douyinLiveWebFetcher

import codecs
import gzip
import hashlib
import random
import re
import string
import subprocess
import threading
import time
import execjs
import urllib.parse
import sys
from contextlib import contextmanager
from unittest.mock import patch

import requests
import websocket
from py_mini_racer import MiniRacer

from .ac_signature import get__ac_signature
from .protobuf.douyin import *

from urllib3.util.url import parse_url

# 设置标准输出编码为UTF-8，避免emoji编码错误
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


def execute_js(js_file: str):
    """
    执行 JavaScript 文件
    :param js_file: JavaScript 文件路径
    :return: 执行结果
    """
    with open(js_file, 'r', encoding='utf-8') as file:
        js_code = file.read()
    
    ctx = execjs.compile(js_code)
    return ctx


@contextmanager
def patched_popen_encoding(encoding='utf-8'):
    original_popen_init = subprocess.Popen.__init__
    
    def new_popen_init(self, *args, **kwargs):
        kwargs['encoding'] = encoding
        original_popen_init(self, *args, **kwargs)
    
    with patch.object(subprocess.Popen, '__init__', new_popen_init):
        yield


def generateSignature(wss, script_file=None):
    """
    出现gbk编码问题则修改 python模块subprocess.py的源码中Popen类的__init__函数参数encoding值为 "utf-8"
    """
    # 如果没有提供script_file，使用默认路径
    if script_file is None:
        import os
        script_file = os.path.join(os.path.dirname(__file__), 'sign.js')
    
    params = ("live_id,aid,version_code,webcast_sdk_version,"
              "room_id,sub_room_id,sub_channel_id,did_rule,"
              "user_unique_id,device_platform,device_type,ac,"
              "identity").split(',')
    wss_params = urllib.parse.urlparse(wss).query.split('&')
    wss_maps = {i.split('=')[0]: i.split("=")[-1] for i in wss_params}
    tpl_params = [f"{i}={wss_maps.get(i, '')}" for i in params]
    param = ','.join(tpl_params)
    md5 = hashlib.md5()
    md5.update(param.encode())
    md5_param = md5.hexdigest()
    
    with codecs.open(script_file, 'r', encoding='utf8') as f:
        script = f.read()
    
    ctx = MiniRacer()
    ctx.eval(script)
    
    try:
        signature = ctx.call("get_sign", md5_param)
        return signature
    except Exception as e:
        print(e)
    
    # 以下代码对应js脚本为sign_v0.js
    # context = execjs.compile(script)
    # with patched_popen_encoding(encoding='utf-8'):
    #     ret = context.call('getSign', {'X-MS-STUB': md5_param})
    # return ret.get('X-Bogus')


def generateMsToken(length=182):
    """
    产生请求头部cookie中的msToken字段，其实为随机的107位字符
    :param length:字符位数
    :return:msToken
    """
    random_str = ''
    base_str = string.ascii_letters + string.digits + '-_'
    _len = len(base_str) - 1
    for _ in range(length):
        random_str += base_str[random.randint(0, _len)]
    return random_str


class DouyinLiveWebFetcher:
    
    def __init__(self, live_id, abogus_file='a_bogus.js'):
        """
        直播间弹幕抓取对象
        :param live_id: 直播间的直播id，打开直播间web首页的链接如：https://live.douyin.com/261378947940，
                        其中的261378947940即是live_id
        """
        self.abogus_file = abogus_file
        self.__ttwid = None
        self.__room_id = None
        self.session = requests.Session()
        self.live_id = live_id
        self.host = "https://www.douyin.com/"
        self.live_url = "https://live.douyin.com/"
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0"
        self.headers = {
            'User-Agent': self.user_agent
        }
    
    def start(self):
        self._connectWebSocket()
    
    def stop(self):
        self.ws.close()
    
    @property
    def ttwid(self):
        """
        产生请求头部cookie中的ttwid字段，访问抖音网页版直播间首页可以获取到响应cookie中的ttwid
        :return: ttwid
        """
        if self.__ttwid:
            return self.__ttwid
        headers = {
            "User-Agent": self.user_agent,
        }
        # 添加重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(self.live_url, headers=headers, timeout=10)
                response.raise_for_status()
                self.__ttwid = response.cookies.get('ttwid')
                print(f"【√】成功获取ttwid: {self.__ttwid}")
                return self.__ttwid
            except Exception as err:
                print(f"【X】获取ttwid失败 (尝试 {attempt + 1}/{max_retries}): {err}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # 等待2秒后重试
                else:
                    print("【X】获取ttwid失败，已达到最大重试次数")
                    raise
    
    @property
    def room_id(self):
        """
        根据直播间的地址获取到真正的直播间roomId，有时会有错误，可以重试请求解决
        :return:room_id
        """
        if self.__room_id:
            return self.__room_id
        url = self.live_url + self.live_id
        headers = {
            "User-Agent": self.user_agent,
            "cookie": f"ttwid={self.ttwid}&msToken={generateMsToken()}; __ac_nonce=0123407cc00a9e438deb4",
        }
        # 添加重试机制
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                match = re.search(r'roomId\\":\\"(\d+)\\"', response.text)
                if match is None or len(match.groups()) < 1:
                    print("【X】未找到roomId")
                    raise ValueError("未找到roomId")
                
                self.__room_id = match.group(1)
                print(f"【√】成功获取room_id: {self.__room_id}")
                return self.__room_id
            except Exception as err:
                print(f"【X】获取room_id失败 (尝试 {attempt + 1}/{max_retries}): {err}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # 等待2秒后重试
                else:
                    print("【X】获取room_id失败，已达到最大重试次数")
                    raise
    
    def get_ac_nonce(self):
        """
        获取 __ac_nonce
        """
        resp_cookies = self.session.get(self.host, headers=self.headers).cookies
        return resp_cookies.get("__ac_nonce")
    
    def get_ac_signature(self, __ac_nonce: str = None) -> str:
        """
        获取 __ac_signature
        """
        __ac_signature = get__ac_signature(self.host[8:], __ac_nonce, self.user_agent)
        self.session.cookies.set("__ac_signature", __ac_signature)
        return __ac_signature
    
    def get_a_bogus(self, url_params: dict):
        """
        获取 a_bogus
        """
        url = urllib.parse.urlencode(url_params)
        ctx = execute_js(self.abogus_file)
        _a_bogus = ctx.call("get_ab", url, self.user_agent)
        return _a_bogus
    
    def get_room_status(self):
        """
        获取直播间开播状态:
        room_status: 2 直播已结束
        room_status: 0 直播进行中
        """
        msToken = generateMsToken()
        nonce = self.get_ac_nonce()
        signature = self.get_ac_signature(nonce)
        url = ('https://live.douyin.com/webcast/room/web/enter/?aid=6383'
               '&app_name=douyin_web&live_id=1&device_platform=web&language=zh-CN&enter_from=page_refresh'
               '&cookie_enabled=true&screen_width=5120&screen_height=1440&browser_language=zh-CN&browser_platform=Win32'
               '&browser_name=Edge&browser_version=140.0.0.0'
               f'&web_rid={self.live_id}'
               f'&room_id_str={self.room_id}'
               '&enter_source=&is_need_double_stream=false&insert_task_id=&live_reason=&msToken=' + msToken)
        query = parse_url(url).query
        params = {i[0]: i[1] for i in [j.split('=') for j in query.split('&')]}
        a_bogus = self.get_a_bogus(params)  # 计算a_bogus,成功率不是100%，出现失败时重试即可
        url += f"&a_bogus={a_bogus}"
        headers = self.headers.copy()
        headers.update({
            'Referer': f'https://live.douyin.com/{self.live_id}',
            'Cookie': f'ttwid={self.ttwid};__ac_nonce={nonce}; __ac_signature={signature}',
        })
        resp = self.session.get(url, headers=headers)
        data = resp.json().get('data')
        if data:
            room_status = data.get('room_status')
            user = data.get('user')
            user_id = user.get('id_str')
            nickname = user.get('nickname')
            print(f"【{nickname}】[{user_id}]直播间：{['正在直播', '已结束'][bool(room_status)]}.")
    
    def _connectWebSocket(self):
        """
        连接抖音直播间websocket服务器，请求直播间数据
        """
        wss = ("wss://webcast100-ws-web-lq.douyin.com/webcast/im/push/v2/?app_name=douyin_web"
               "&version_code=180800&webcast_sdk_version=1.0.14-beta.0"
               "&update_version_code=1.0.14-beta.0&compress=gzip&device_platform=web&cookie_enabled=true"
               "&screen_width=1536&screen_height=864&browser_language=zh-CN&browser_platform=Win32"
               "&browser_name=Mozilla"
               "&browser_version=5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)%20AppleWebKit/537.36%20(KHTML,"
               "%20like%20Gecko)%20Chrome/126.0.0.0%20Safari/537.36"
               "&browser_online=true&tz_name=Asia/Shanghai"
               "&cursor=d-1_u-1_fh-7392091211001140287_t-1721106114633_r-1"
               f"&internal_ext=internal_src:dim|wss_push_room_id:{self.room_id}|wss_push_did:7319483754668557238"
               f"|first_req_ms:1721106114541|fetch_time:1721106114633|seq:1|wss_info:0-1721106114633-0-0|"
               f"wrds_v:7392094459690748497"
               f"&host=https://live.douyin.com&aid=6383&live_id=1&did_rule=3&endpoint=live_pc&support_wrds=1"
               f"&user_unique_id=7319483754668557238&im_path=/webcast/im/fetch/&identity=audience"
               f"&need_persist_msg_count=15&insert_task_id=&live_reason=&room_id={self.room_id}&heartbeatDuration=0")
        
        signature = generateSignature(wss)
        wss += f"&signature={signature}"
        
        headers = {
            "cookie": f"ttwid={self.ttwid}",
            'user-agent': self.user_agent,
        }
        print(f"【调试】WebSocket URL: {wss[:100]}...")
        print(f"【调试】Headers: {headers}")
        
        self.ws = websocket.WebSocketApp(wss,
                                         header=headers,
                                         on_open=self._wsOnOpen,
                                         on_message=self._wsOnMessage,
                                         on_error=self._wsOnError,
                                         on_close=self._wsOnClose,
                                         on_ping=self._wsOnPing,
                                         on_pong=self._wsOnPong)
        try:
            # 添加超时设置，避免无限等待
            print("【√】开始连接WebSocket...")
            # 增加ping间隔和超时时间，避免频繁超时
            # 设置为0禁用自动ping，我们使用应用层心跳
            self.ws.run_forever(
                ping_interval=30,  # 每30秒发送一次ping
                ping_timeout=15,   # ping超时时间15秒
                skip_utf8_validation=True
            )
        except Exception as e:
            print(f"【X】WebSocket运行异常: {e}")
            self.stop()
            raise
    
    def _sendHeartbeat(self):
        """
        发送心跳包 - 使用抖音协议的心跳格式
        """
        while True:
            try:
                # 使用抖音协议的心跳包格式
                heartbeat = PushFrame(payload_type='hb').SerializeToString()
                # 使用BINARY模式发送，而不是PING
                self.ws.send(heartbeat, websocket.ABNF.OPCODE_BINARY)
                print("【√】发送心跳包")
            except Exception as e:
                print(f"【X】心跳包发送失败: {e}")
                break
            else:
                # 增加心跳间隔到10秒，避免过于频繁
                time.sleep(10)
    
    def _wsOnOpen(self, ws):
        """
        连接建立成功
        """
        print("=" * 60)
        print("【√】WebSocket连接成功，开始接收直播间消息")
        print(f"【√】直播间ID: {self.live_id}, Room ID: {self.room_id}")
        print(f"【√】ttwid: {self.ttwid}")
        print("=" * 60)
        threading.Thread(target=self._sendHeartbeat, daemon=True).start()
    
    def _wsOnMessage(self, ws, message):
        """
        接收到数据
        :param ws: websocket实例
        :param message: 数据
        """
        print(f"【→】收到原始WebSocket消息，大小: {len(message)} 字节")
        
        try:
            # 根据proto结构体解析对象
            package = PushFrame().parse(message)
            print(f"【√】PushFrame解析成功，log_id: {package.log_id}")
            
            response = Response().parse(gzip.decompress(package.payload))
            print(f"【√】Response解析成功，消息数量: {len(response.messages_list)}")
            
            # 返回直播间服务器链接存活确认消息，便于持续获取数据
            if response.need_ack:
                ack = PushFrame(log_id=package.log_id,
                                payload_type='ack',
                                payload=response.internal_ext.encode('utf-8')
                                ).SerializeToString()
                ws.send(ack, websocket.ABNF.OPCODE_BINARY)
                print(f"【√】已发送ACK确认")
            
            # 根据消息类别解析消息体
            for msg in response.messages_list:
                method = msg.method
                # 只打印重要消息类型，减少日志噪音
                important_types = ['WebcastChatMessage', 'WebcastGiftMessage', 'WebcastLikeMessage',
                                 'WebcastMemberMessage', 'WebcastSocialMessage', 'WebcastControlMessage']
                if method in important_types:
                    print(f"【收到消息】类型: {method}")
                
                try:
                    handler = {
                        'WebcastChatMessage': self._parseChatMsg,  # 聊天消息
                        'WebcastGiftMessage': self._parseGiftMsg,  # 礼物消息
                        'WebcastLikeMessage': self._parseLikeMsg,  # 点赞消息
                        'WebcastMemberMessage': self._parseMemberMsg,  # 进入直播间消息
                        'WebcastSocialMessage': self._parseSocialMsg,  # 关注消息
                        'WebcastRoomUserSeqMessage': self._parseRoomUserSeqMsg,  # 直播间统计
                        'WebcastFansclubMessage': self._parseFansclubMsg,  # 粉丝团消息
                        'WebcastControlMessage': self._parseControlMsg,  # 直播间状态消息
                        'WebcastEmojiChatMessage': self._parseEmojiChatMsg,  # 聊天表情包消息
                        'WebcastRoomStatsMessage': self._parseRoomStatsMsg,  # 直播间统计信息
                        'WebcastRoomMessage': self._parseRoomMsg,  # 直播间信息
                        'WebcastRoomRankMessage': self._parseRankMsg,  # 直播间排行榜信息
                        'WebcastRoomStreamAdaptationMessage': self._parseRoomStreamAdaptationMsg,  # 直播间流配置
                        'WebcastInRoomBannerMessage': self._parseInRoomBannerMsg,  # 直播间横幅
                        'WebcastGiftSortMessage': self._parseGiftSortMsg,  # 礼物排行
                        'WebcastRanklistHourEntranceMessage': self._parseRanklistHourEntranceMsg,  # 小时榜入口
                    }.get(method)
                    
                    if handler:
                        handler(msg.payload)
                    else:
                        # 静默忽略未知消息类型，避免日志过多
                        pass
                        
                except Exception as e:
                    if method in important_types:
                        print(f"【X】处理消息失败 {method}: {e}")
                    
        except Exception as e:
            print(f"【X】解析WebSocket消息失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _wsOnError(self, ws, error):
        print("=" * 60)
        print(f"【X】WebSocket错误: {error}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
    
    def _wsOnPing(self, ws, message):
        """
        收到服务器的ping消息，自动回复pong
        """
        print("【√】收到服务器ping，自动回复pong")
    
    def _wsOnPong(self, ws, message):
        """
        收到服务器的pong响应
        """
        print("【√】收到服务器pong响应")
    
    def _wsOnClose(self, ws, *args):
        try:
            self.get_room_status()
        except Exception as e:
            print(f"【X】获取直播间状态失败: {e}")
        print("WebSocket connection closed.")
    
    def _parseChatMsg(self, payload):
        """聊天消息"""
        try:
            message = ChatMessage().parse(payload)
            user_name = message.user.nick_name
            user_id = message.user.id
            content = message.content
            print(f"【聊天msg】[{user_id}]{user_name}: {content}")
        except Exception as e:
            print(f"【X】解析聊天消息失败: {e}")
    
    def _parseGiftMsg(self, payload):
        """礼物消息"""
        message = GiftMessage().parse(payload)
        user_name = message.user.nick_name
        gift_name = message.gift.name
        gift_cnt = message.combo_count
        print(f"【礼物msg】{user_name} 送出了 {gift_name}x{gift_cnt}")
    
    def _parseLikeMsg(self, payload):
        '''点赞消息'''
        try:
            message = LikeMessage().parse(payload)
            user_name = message.user.nick_name
            count = message.count
            print(f"【点赞msg】{user_name} 点了{count}个赞")
        except Exception as e:
            print(f"【X】解析点赞消息失败: {e}")
    
    def _parseMemberMsg(self, payload):
        '''进入直播间消息'''
        try:
            message = MemberMessage().parse(payload)
            user_name = message.user.nick_name
            user_id = message.user.id
            gender = ["女", "男"][message.user.gender] if message.user.gender in [0, 1] else "未知"
            print(f"【进场msg】[{user_id}][{gender}]{user_name} 进入了直播间")
        except Exception as e:
            print(f"【X】解析进场消息失败: {e}")
    
    def _parseSocialMsg(self, payload):
        '''关注消息'''
        message = SocialMessage().parse(payload)
        user_name = message.user.nick_name
        user_id = message.user.id
        print(f"【关注msg】[{user_id}]{user_name} 关注了主播")
    
    def _parseRoomUserSeqMsg(self, payload):
        '''直播间统计'''
        message = RoomUserSeqMessage().parse(payload)
        current = message.total
        total = message.total_pv_for_anchor
        print(f"【统计msg】当前观看人数: {current}, 累计观看人数: {total}")
    
    def _parseFansclubMsg(self, payload):
        '''粉丝团消息'''
        message = FansclubMessage().parse(payload)
        content = message.content
        print(f"【粉丝团msg】 {content}")
    
    def _parseEmojiChatMsg(self, payload):
        '''聊天表情包消息'''
        message = EmojiChatMessage().parse(payload)
        emoji_id = message.emoji_id
        user = message.user
        common = message.common
        default_content = message.default_content
        print(f"【聊天表情包id】 {emoji_id},user：{user},common:{common},default_content:{default_content}")
    
    def _parseRoomMsg(self, payload):
        message = RoomMessage().parse(payload)
        common = message.common
        room_id = common.room_id
        print(f"【直播间msg】直播间id:{room_id}")
    
    def _parseRoomStatsMsg(self, payload):
        message = RoomStatsMessage().parse(payload)
        display_long = message.display_long
        print(f"【直播间统计msg】{display_long}")
    
    def _parseRankMsg(self, payload):
        message = RoomRankMessage().parse(payload)
        ranks_list = message.ranks_list
        print(f"【直播间排行榜msg】{ranks_list}")
    
    def _parseControlMsg(self, payload):
        '''直播间状态消息'''
        message = ControlMessage().parse(payload)
        
        if message.status == 3:
            print("直播间已结束")
            self.stop()
    
    def _parseRoomStreamAdaptationMsg(self, payload):
        message = RoomStreamAdaptationMessage().parse(payload)
        adaptationType = message.adaptation_type
        print(f'直播间adaptation: {adaptationType}')
    
    def _parseInRoomBannerMsg(self, payload):
        '''直播间横幅消息 - 暂不处理'''
        pass
    
    def _parseGiftSortMsg(self, payload):
        '''礼物排行消息 - 暂不处理'''
        pass
    
    def _parseRanklistHourEntranceMsg(self, payload):
        '''小时榜入口消息 - 暂不处理'''
        pass
