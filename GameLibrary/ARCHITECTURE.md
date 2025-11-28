# 游戏库架构设计

## 概述

游戏库是一个独立的游戏模块管理系统，将游戏从平台中完全解耦，每个游戏作为独立的模块存储和管理。

## 设计原则

1. **完全解耦**: 游戏与平台完全分离，互不依赖
2. **标准化接口**: 所有游戏遵循统一的接口规范
3. **独立部署**: 每个游戏可以独立开发、测试和部署
4. **热插拔**: 支持动态加载和卸载游戏
5. **版本管理**: 每个游戏独立版本控制

## 目录结构

```
GameLibrary/
├── ARCHITECTURE.md              # 架构设计文档
├── README.md                    # 游戏库使用说明
├── game-registry.json           # 游戏注册表
├── game-loader.js               # 游戏加载器（前端）
├── game-manager.py              # 游戏管理器（后端）
├── templates/                   # 游戏模板
│   └── game-template/           # 标准游戏模板
└── games/                       # 游戏存储目录
    ├── fortune-game/            # 巫女占卜游戏
    │   ├── game.json           # 游戏配置文件
    │   ├── README.md           # 游戏说明
    │   ├── frontend/           # 前端资源
    │   │   ├── index.html
    │   │   ├── css/
    │   │   ├── js/
    │   │   └── assets/
    │   └── backend/            # 后端服务（可选）
    │       ├── api.py
    │       └── requirements.txt
    └── [other-games]/          # 其他游戏...
```

## 游戏配置规范 (game.json)

每个游戏必须包含一个 `game.json` 配置文件：

```json
{
  "id": "fortune-game",
  "name": "巫女占卜",
  "version": "1.0.0",
  "description": "体验神秘的占卜之旅，探索你的运势",
  "author": "XMGamer Team",
  "icon": "assets/icon.png",
  "thumbnail": "assets/thumbnail.gif",
  "tags": ["占卜", "互动", "直播"],
  "category": "entertainment",
  "type": "iframe",
  "entry": {
    "frontend": "frontend/index.html",
    "backend": "backend/api.py"
  },
  "api": {
    "prefix": "/api/fortune",
    "endpoints": [
      {
        "path": "/chat",
        "method": "POST",
        "description": "占卜聊天接口"
      },
      {
        "path": "/live/start",
        "method": "POST",
        "description": "开始监听直播间"
      }
    ]
  },
  "websocket": {
    "enabled": true,
    "events": ["fortune_chat", "join", "leave"]
  },
  "dependencies": {
    "frontend": ["socket.io-client@4.5.4"],
    "backend": ["Flask-SocketIO>=5.3.5", "python-socketio>=5.10.0"]
  },
  "permissions": ["websocket", "api"],
  "settings": {
    "autoFlipDelay": 10000,
    "maxPlayers": 100
  }
}
```

## 游戏注册表 (game-registry.json)

全局游戏注册表，记录所有已注册的游戏：

```json
{
  "version": "1.0.0",
  "games": [
    {
      "id": "fortune-game",
      "name": "巫女占卜",
      "version": "1.0.0",
      "path": "games/fortune-game",
      "enabled": true,
      "installedAt": "2024-11-25T00:00:00Z",
      "lastUpdated": "2024-11-25T00:00:00Z"
    }
  ]
}
```

## 游戏加载流程

### 前端加载流程

1. 平台启动时读取 `game-registry.json`
2. 根据注册表加载游戏元数据
3. 在游戏市场展示游戏卡片
4. 用户点击游戏时，通过 `game-loader.js` 动态加载游戏
5. 根据游戏类型（iframe/component）选择加载方式

### 后端加载流程

1. 服务器启动时扫描游戏目录
2. 读取每个游戏的 `game.json`
3. 动态注册游戏API路由
4. 初始化游戏WebSocket事件
5. 加载游戏依赖服务

## API接口规范

### 游戏管理API

```
GET  /api/games              # 获取所有游戏列表
GET  /api/games/:id          # 获取指定游戏信息
POST /api/games/:id/install  # 安装游戏
POST /api/games/:id/uninstall # 卸载游戏
POST /api/games/:id/enable   # 启用游戏
POST /api/games/:id/disable  # 禁用游戏
```

### 游戏专属API

每个游戏的API路由前缀为 `/api/games/:gameId/`，例如：
- `/api/games/fortune-game/chat`
- `/api/games/fortune-game/live/start`

## 游戏类型

### 1. iframe类型
- 游戏在独立的iframe中运行
- 完全隔离，互不影响
- 适合复杂的独立游戏

### 2. component类型
- 游戏作为组件直接集成到平台
- 共享平台资源和状态
- 适合轻量级小游戏

## 通信机制

### 平台与游戏通信

使用 `postMessage` API 进行跨iframe通信：

```javascript
// 平台发送消息给游戏
gameIframe.contentWindow.postMessage({
  type: 'PLATFORM_EVENT',
  data: { userId: '123', token: 'xxx' }
}, '*');

// 游戏发送消息给平台
window.parent.postMessage({
  type: 'GAME_EVENT',
  data: { action: 'score_update', score: 100 }
}, '*');
```

### 游戏与后端通信

1. **HTTP API**: 标准RESTful API
2. **WebSocket**: 实时双向通信
3. **Socket.IO**: 支持房间和事件机制

## 安全机制

1. **沙箱隔离**: iframe游戏运行在沙箱环境
2. **权限控制**: 游戏需要声明所需权限
3. **API鉴权**: 所有API请求需要验证
4. **资源限制**: 限制游戏资源使用

## 版本管理

1. 每个游戏独立版本号（遵循语义化版本）
2. 支持游戏热更新
3. 保留历史版本回滚能力
4. 自动检测版本冲突

## 开发工作流

### 创建新游戏

1. 复制游戏模板
2. 修改 `game.json` 配置
3. 开发游戏功能
4. 测试游戏
5. 注册到游戏库

### 更新游戏

1. 修改游戏代码
2. 更新版本号
3. 测试兼容性
4. 发布更新

### 删除游戏

1. 从注册表移除
2. 清理游戏文件
3. 清理相关数据

## 性能优化

1. **懒加载**: 游戏按需加载
2. **资源缓存**: 缓存游戏资源
3. **预加载**: 预加载热门游戏
4. **CDN加速**: 静态资源使用CDN

## 扩展性

1. 支持第三方游戏接入
2. 支持游戏市场
3. 支持游戏评分和评论
4. 支持游戏数据分析

## 迁移计划

### 阶段1: 基础架构搭建
- 创建游戏库目录结构
- 实现游戏加载器
- 实现游戏管理器

### 阶段2: 游戏迁移
- 迁移巫女占卜游戏
- 测试游戏功能
- 验证通信机制

### 阶段3: 平台集成
- 更新平台代码
- 实现游戏市场
- 完善文档

### 阶段4: 优化和扩展
- 性能优化
- 添加新功能
- 支持更多游戏