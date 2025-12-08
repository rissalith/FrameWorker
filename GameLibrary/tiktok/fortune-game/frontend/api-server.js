/**
 * TikTok Fortune Game - API Server
 * 使用 tiktok-live-connector 连接 TikTok 直播间
 */

import express from 'express';
import cors from 'cors';
import http from 'http';
import { Server } from 'socket.io';
import { TikTokLiveConnection, WebcastEvent, ControlEvent } from 'tiktok-live-connector';
import { HttpsProxyAgent } from 'https-proxy-agent';

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

// 中间件
app.use(cors());
app.use(express.json());

// 代理配置 - 如果需要可以修改
const PROXY_URL = process.env.PROXY_URL || 'http://127.0.0.1:7897';
const USE_PROXY = process.env.USE_PROXY !== 'false'; // 默认使用代理

// 存储活跃的直播间连接
const activeRooms = new Map();

/**
 * TikTok 直播间监控类
 */
class TikTokLiveRoomMonitor {
    constructor(uniqueId, io) {
        this.uniqueId = uniqueId;
        this.io = io;
        this.connection = null;
        this.stats = {
            messageCount: 0,
            giftCount: 0,
            memberCount: 0,
            likeCount: 0
        };
    }

    start() {
        console.log(`[√] 启动 TikTok 直播间监控: @${this.uniqueId}`);

        // 创建代理配置
        const options = {
            processInitialData: true,
            enableExtendedGiftInfo: true,
            fetchRoomInfoOnConnect: true,
            webClientOptions: {
                timeout: 30000
            },
            wsClientOptions: {
                timeout: 30000
            }
        };

        // 如果启用代理
        if (USE_PROXY) {
            const agent = new HttpsProxyAgent(PROXY_URL);
            options.webClientOptions.httpsAgent = agent;
            options.wsClientOptions.agent = agent;
            console.log(`[√] 使用代理: ${PROXY_URL}`);
        }

        this.connection = new TikTokLiveConnection(this.uniqueId, options);

        // 连接成功
        this.connection.on(ControlEvent.CONNECTED, (state) => {
            console.log(`[√] 已连接到 TikTok 直播间: @${this.uniqueId}`);
            console.log(`[√] Room ID: ${state.roomId}`);

            this.io.to(this.uniqueId).emit('live_message', {
                type: 'connected',
                live_id: this.uniqueId,
                room_id: state.roomId,
                message: `已连接到直播间 @${this.uniqueId}`
            });
        });

        // 断开连接
        this.connection.on(ControlEvent.DISCONNECTED, () => {
            console.log(`[X] 已断开 TikTok 直播间: @${this.uniqueId}`);
            this.io.to(this.uniqueId).emit('live_message', {
                type: 'disconnected',
                live_id: this.uniqueId,
                message: '直播间连接已断开'
            });
        });

        // 直播结束
        this.connection.on(ControlEvent.STREAM_END, () => {
            console.log(`[X] 直播已结束: @${this.uniqueId}`);
            this.io.to(this.uniqueId).emit('live_message', {
                type: 'stream_end',
                live_id: this.uniqueId,
                message: '直播已结束'
            });
        });

        // 错误处理
        this.connection.on(ControlEvent.ERROR, (err) => {
            console.error(`[X] TikTok 连接错误: ${err.message || err}`);
        });

        // 弹幕消息
        this.connection.on(WebcastEvent.CHAT, (data) => {
            this.stats.messageCount++;
            const username = data.user?.uniqueId || data.uniqueId || 'Unknown';
            const nickname = data.user?.nickname || username;
            const userId = data.user?.userId || '';
            const avatarUrl = data.user?.profilePictureUrl || '';

            console.log(`[弹幕] ${nickname}: ${data.comment}`);
            if (avatarUrl) {
                console.log(`[头像] ${nickname}: ${avatarUrl}`);
            } else {
                console.log(`[头像] ${nickname}: 无头像数据`);
            }

            this.io.to(this.uniqueId).emit('live_message', {
                type: 'chat',
                live_id: this.uniqueId,
                user_id: userId,
                user_name: nickname || username,
                user_avatar: data.user?.profilePictureUrl || '',
                content: data.comment,
                timestamp: Math.floor(Date.now() / 1000)
            });
        });

        // 礼物
        this.connection.on(WebcastEvent.GIFT, (data) => {
            const username = data.user?.uniqueId || data.uniqueId || 'Unknown';
            const nickname = data.user?.nickname || username;

            // 只处理礼物连击结束或非连击礼物
            if (data.giftType !== 1 || data.repeatEnd) {
                this.stats.giftCount++;
                const giftName = data.giftName || `礼物${data.giftId}`;
                const giftCount = data.repeatCount || 1;
                const diamondCount = data.diamondCount || 0;

                console.log(`[礼物] ${nickname} 送出 ${giftName} x${giftCount}`);

                this.io.to(this.uniqueId).emit('live_message', {
                    type: 'gift',
                    live_id: this.uniqueId,
                    user_id: data.user?.userId || '',
                    user_name: nickname || username,
                    user_avatar: data.user?.profilePictureUrl || '',
                    gift_id: data.giftId,
                    gift_name: giftName,
                    gift_count: giftCount,
                    diamond_count: diamondCount,
                    gift_image: data.giftPictureUrl || '',
                    timestamp: Math.floor(Date.now() / 1000)
                });
            }
        });

        // 用户加入
        this.connection.on(WebcastEvent.MEMBER, (data) => {
            this.stats.memberCount++;
            const username = data.user?.uniqueId || data.uniqueId || 'Unknown';
            const nickname = data.user?.nickname || username;

            console.log(`[加入] ${nickname} 进入直播间`);

            this.io.to(this.uniqueId).emit('live_message', {
                type: 'member',
                live_id: this.uniqueId,
                user_id: data.user?.userId || '',
                user_name: nickname || username,
                user_avatar: data.user?.profilePictureUrl || '',
                timestamp: Math.floor(Date.now() / 1000)
            });
        });

        // 点赞
        this.connection.on(WebcastEvent.LIKE, (data) => {
            this.stats.likeCount += data.likeCount || 1;
            const username = data.user?.uniqueId || data.uniqueId || 'Unknown';
            const nickname = data.user?.nickname || username;

            this.io.to(this.uniqueId).emit('live_message', {
                type: 'like',
                live_id: this.uniqueId,
                user_id: data.user?.userId || '',
                user_name: nickname || username,
                user_avatar: data.user?.profilePictureUrl || '',
                count: data.likeCount || 1,
                total: data.totalLikeCount || 0,
                timestamp: Math.floor(Date.now() / 1000)
            });
        });

        // 关注
        this.connection.on(WebcastEvent.FOLLOW, (data) => {
            const username = data.user?.uniqueId || data.uniqueId || 'Unknown';
            const nickname = data.user?.nickname || username;
            console.log(`[关注] ${nickname} 关注了主播`);

            this.io.to(this.uniqueId).emit('live_message', {
                type: 'follow',
                live_id: this.uniqueId,
                user_id: data.user?.userId || '',
                user_name: nickname || username,
                user_avatar: data.user?.profilePictureUrl || '',
                timestamp: Math.floor(Date.now() / 1000)
            });
        });

        // 分享
        this.connection.on(WebcastEvent.SHARE, (data) => {
            const username = data.user?.uniqueId || data.uniqueId || 'Unknown';
            const nickname = data.user?.nickname || username;
            console.log(`[分享] ${nickname} 分享了直播间`);

            this.io.to(this.uniqueId).emit('live_message', {
                type: 'share',
                live_id: this.uniqueId,
                user_id: data.user?.userId || '',
                user_name: nickname || username,
                user_avatar: data.user?.profilePictureUrl || '',
                timestamp: Math.floor(Date.now() / 1000)
            });
        });

        // 观众数量更新
        this.connection.on(WebcastEvent.ROOM_USER, (data) => {
            if (data.viewerCount) {
                this.io.to(this.uniqueId).emit('live_message', {
                    type: 'room_stats',
                    live_id: this.uniqueId,
                    viewer_count: data.viewerCount,
                    timestamp: Date.now()
                });
            }
        });

        // 开始连接
        return this.connection.connect()
            .then((state) => {
                console.log(`[√] TikTok 直播间连接成功: @${this.uniqueId}, Room ID: ${state.roomId}`);
                return state;
            })
            .catch((err) => {
                console.error(`[X] TikTok 直播间连接失败: ${err.message || err}`);
                throw err;
            });
    }

    stop() {
        if (this.connection) {
            console.log(`[X] 停止 TikTok 直播间监控: @${this.uniqueId}`);
            this.connection.disconnect();
            this.connection = null;
        }
    }

    getStats() {
        return this.stats;
    }
}

// API路由
app.get('/', (req, res) => {
    res.json({
        status: 'running',
        message: 'TikTok 直播间监控服务正在运行',
        version: '2.0.0',
        platform: 'TikTok',
        proxy: USE_PROXY ? PROXY_URL : 'disabled',
        active_rooms: Array.from(activeRooms.keys())
    });
});

app.post('/api/live/start', async (req, res) => {
    try {
        let { live_id } = req.body;

        if (!live_id) {
            return res.status(400).json({
                success: false,
                message: '缺少直播间ID (TikTok用户名)'
            });
        }

        // 清理用户名 - 移除 @ 符号
        live_id = live_id.replace(/^@/, '').trim();

        // 如果已经在监听，直接返回成功
        if (activeRooms.has(live_id)) {
            return res.json({
                success: true,
                message: `直播间 @${live_id} 已在监听中`,
                live_id: live_id
            });
        }

        // 创建监控器
        const monitor = new TikTokLiveRoomMonitor(live_id, io);
        activeRooms.set(live_id, monitor);

        try {
            const state = await monitor.start();
            console.log(`[√] 开始监听 TikTok 直播间: @${live_id}`);

            res.json({
                success: true,
                message: `成功开始监听 TikTok 直播间 @${live_id}`,
                live_id: live_id,
                room_id: state.roomId
            });
        } catch (error) {
            activeRooms.delete(live_id);
            throw error;
        }
    } catch (error) {
        console.error('[X] 启动失败:', error);
        res.status(500).json({
            success: false,
            message: `启动失败: ${error.message || error}`
        });
    }
});

app.post('/api/live/stop', (req, res) => {
    try {
        let { live_id } = req.body;

        if (!live_id) {
            return res.status(400).json({
                success: false,
                message: '缺少直播间ID'
            });
        }

        live_id = live_id.replace(/^@/, '').trim();

        const monitor = activeRooms.get(live_id);
        if (monitor) {
            monitor.stop();
            activeRooms.delete(live_id);
            console.log(`[√] 停止监听直播间: @${live_id}`);
        }

        res.json({
            success: true,
            message: `已停止监听直播间 @${live_id}`
        });
    } catch (error) {
        console.error('[X] 停止失败:', error);
        res.status(500).json({
            success: false,
            message: `停止失败: ${error.message}`
        });
    }
});

app.get('/api/live/status', (req, res) => {
    const rooms = [];
    for (const [id, monitor] of activeRooms) {
        rooms.push({
            live_id: id,
            stats: monitor.getStats()
        });
    }

    res.json({
        success: true,
        active_rooms: rooms,
        count: activeRooms.size
    });
});

// 设置代理
app.post('/api/config/proxy', (req, res) => {
    const { proxy_url, enabled } = req.body;

    if (proxy_url) {
        process.env.PROXY_URL = proxy_url;
    }
    if (typeof enabled === 'boolean') {
        process.env.USE_PROXY = enabled.toString();
    }

    res.json({
        success: true,
        message: '代理配置已更新',
        proxy_url: process.env.PROXY_URL || PROXY_URL,
        enabled: process.env.USE_PROXY !== 'false'
    });
});

// Socket.IO事件处理
io.on('connection', (socket) => {
    console.log(`[√] 客户端已连接: ${socket.id}`);

    socket.emit('connected', { message: '已连接到 TikTok 直播监控服务器' });

    socket.on('join', (liveId) => {
        const cleanId = liveId.replace(/^@/, '').trim();
        socket.join(cleanId);
        console.log(`[√] 客户端 ${socket.id} 加入房间: @${cleanId}`);
        socket.emit('joined', { live_id: cleanId, message: `已加入直播间 @${cleanId}` });
    });

    socket.on('leave', (liveId) => {
        const cleanId = liveId.replace(/^@/, '').trim();
        socket.leave(cleanId);
        console.log(`[X] 客户端 ${socket.id} 离开房间: @${cleanId}`);
        socket.emit('left', { live_id: cleanId, message: `已离开直播间 @${cleanId}` });
    });

    socket.on('disconnect', () => {
        console.log(`[X] 客户端已断开: ${socket.id}`);
    });
});

// 启动服务器
const PORT = process.env.PORT || 5001;
server.listen(PORT, () => {
    console.log('='.repeat(60));
    console.log('TikTok 直播间监控服务启动');
    console.log('='.repeat(60));
    console.log(`服务地址: http://localhost:${PORT}`);
    console.log(`WebSocket: ws://localhost:${PORT}`);
    console.log(`代理状态: ${USE_PROXY ? `启用 (${PROXY_URL})` : '禁用'}`);
    console.log('='.repeat(60));
    console.log('API 端点:');
    console.log('  POST /api/live/start   - 开始监听直播间');
    console.log('  POST /api/live/stop    - 停止监听直播间');
    console.log('  GET  /api/live/status  - 获取监听状态');
    console.log('  POST /api/config/proxy - 配置代理');
    console.log('='.repeat(60));
});

// 优雅退出
process.on('SIGINT', () => {
    console.log('\n[X] 正在关闭服务器...');
    for (const [id, monitor] of activeRooms) {
        monitor.stop();
    }
    activeRooms.clear();
    server.close(() => {
        console.log('[X] 服务器已关闭');
        process.exit(0);
    });
});
