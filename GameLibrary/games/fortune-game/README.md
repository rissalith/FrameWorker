# 巫女占卜游戏

一个神秘的占卜互动游戏，支持直播集成和AI智能对话。

## 游戏简介

巫女占卜是一款基于Web的互动占卜游戏，玩家可以通过抽签的方式获得不同类型的运势预测。游戏采用精美的2D动画效果，配合巫女角色的智能对话系统，为玩家带来沉浸式的占卜体验。

## 功能特性

### 核心功能
- **5种占卜类型**: 日常、爱情、财富、事业、健康
- **5个签级**: 上上签、上签、中签、下签、下下签
- **精美动画**: 2D卡片翻转动画和粒子效果
- **智能对话**: 巫女莉莉AI对话系统
- **权重调整**: 可自定义各签级的出现概率

### 直播功能
- **弹幕集成**: 支持抖音直播间弹幕实时显示
- **礼物映射**: 直播礼物自动映射到占卜类型
- **队列管理**: 礼物队列和排队系统
- **实时互动**: 观众可通过礼物参与占卜

### 技术特性
- **响应式设计**: 支持手机和电脑端
- **WebSocket通信**: 实时双向通信
- **模块化架构**: 清晰的代码结构
- **可扩展性**: 易于添加新的占卜类型

## 游戏玩法

1. **选择占卜类型**: 点击对应的卡片选择想要占卜的类型
2. **抽签**: 卡片翻转显示占卜结果
3. **查看结果**: 查看签级和详细的占卜描述
4. **与巫女对话**: 可以向巫女莉莉提问获得更多指引
5. **直播互动**: 在直播间通过送礼物参与占卜

## 技术栈

### 前端
- HTML5 Canvas (2D渲染)
- JavaScript ES6+
- Socket.IO Client 4.5.4
- CSS3 动画

### 后端
- Python Flask
- Flask-SocketIO
- WebSocket

## 配置说明

### API配置

游戏的API配置在 `frontend/js/config.js` 中：

```javascript
const API_CONFIG = {
    BASE_URL: 'http://localhost:3000/api/fortune',
    ENDPOINTS: {
        CHAT: '/chat',
        LIVE_START: '/live/start',
        LIVE_STOP: '/live/stop',
        LIVE_STATUS: '/live/status'
    }
};
```

### 游戏设置

默认游戏设置：
- 自动翻回延迟: 10秒
- 最大玩家数: 100
- 默认概率分布: 上上签5%, 上签35%, 中签40%, 下签15%, 下下签5%

## 文件结构

```
fortune-game/
├── game.json                    # 游戏配置文件
├── README.md                    # 游戏说明（本文件）
├── frontend/                    # 前端资源
│   ├── index.html              # 游戏主页面
│   ├── css/                    # 样式文件
│   │   ├── main.css
│   │   ├── animations.css
│   │   ├── witch-dialog.css
│   │   └── ...
│   ├── js/                     # JavaScript文件
│   │   ├── config.js           # 配置文件
│   │   ├── game-main-2d.js     # 游戏主逻辑
│   │   ├── witch-lili-agent.js # AI对话系统
│   │   ├── live/               # 直播相关
│   │   └── utils/              # 工具函数
│   └── assets/                 # 游戏资源
│       └── 待机2.png           # 巫女角色图片
└── backend/                     # 后端服务（可选）
    └── api.py                  # API接口
```

## API接口

### 占卜聊天
```
POST /api/fortune/chat
Content-Type: application/json

{
  "message": "用户消息",
  "username": "用户名",
  "grade": "签级",
  "topic": "占卜类型"
}
```

### 直播控制
```
POST /api/fortune/live/start
POST /api/fortune/live/stop
GET  /api/fortune/live/status
```

## WebSocket事件

### 客户端发送
- `connect`: 连接服务器
- `join`: 加入直播间
- `leave`: 离开直播间
- `fortune_chat`: 发送占卜聊天消息

### 服务器发送
- `connected`: 连接成功
- `joined`: 加入房间成功
- `left`: 离开房间成功
- `fortune_response`: 占卜回复

## 开发指南

### 本地运行

1. 确保后端服务已启动
2. 在浏览器中打开 `frontend/index.html`
3. 开始游戏

### 修改占卜内容

占卜数据存储在以下文件中：
- `js/fortune-data-daily.js` - 日常运势
- `js/fortune-data-love.js` - 爱情运势
- `js/fortune-data-wealth.js` - 财富运势
- `js/fortune-data-career.js` - 事业运势
- `js/fortune-data-health.js` - 健康运势

### 自定义样式

修改 `css/` 目录下的样式文件即可自定义游戏外观。

### 添加新功能

游戏采用模块化设计，可以轻松添加新功能：
1. 在 `js/` 目录下创建新模块
2. 在 `index.html` 中引入模块
3. 在 `game-main-2d.js` 中集成新功能

## 注意事项

1. **浏览器兼容性**: 建议使用现代浏览器（Chrome, Firefox, Edge）
2. **网络连接**: 直播功能需要稳定的网络连接
3. **API地址**: 确保API地址配置正确
4. **跨域问题**: 后端需要配置CORS

## 更新日志

### v1.0.0 (2024-11-25)
- 初始版本发布
- 支持5种占卜类型
- 集成直播功能
- 添加AI对话系统
- 实现权重调整功能

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过Issue联系我们。