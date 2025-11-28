# 游戏库 (GameLibrary)

游戏库是一个独立的游戏模块管理系统，实现游戏与平台的完全解耦。

## 📁 目录结构

```
GameLibrary/
├── ARCHITECTURE.md              # 架构设计文档
├── README.md                    # 使用说明（本文件）
├── game-registry.json           # 游戏注册表
├── game-loader.js               # 游戏加载器（前端）
├── game-manager.py              # 游戏管理器（后端）
└── games/                       # 游戏存储目录
    └── fortune-game/            # 巫女占卜游戏
        ├── game.json           # 游戏配置
        ├── README.md           # 游戏说明
        ├── frontend/           # 前端资源
        └── backend/            # 后端服务（可选）
```

## 🚀 快速开始

### 1. 初始化游戏库

```python
from GameLibrary.game_manager import game_manager

# 初始化游戏管理器
game_manager.init()
```

### 2. 注册游戏到Flask应用

```python
from flask import Flask
from GameLibrary.game_manager import game_manager

app = Flask(__name__)

# 注册游戏管理API
game_api_bp = game_manager.create_api_blueprint()
app.register_blueprint(game_api_bp)
```

### 3. 前端加载游戏

```html
<!-- 引入游戏加载器 -->
<script src="/GameLibrary/game-loader.js"></script>

<script>
// 初始化游戏加载器
await GameLoader.init();

// 获取所有游戏
const games = await GameLoader.getAllGames();

// 加载指定游戏
await GameLoader.loadGame('fortune-game', 'game-container');
</script>
```

## 📦 添加新游戏

### 步骤1: 创建游戏目录

```bash
mkdir -p GameLibrary/games/my-game/frontend
mkdir -p GameLibrary/games/my-game/backend
```

### 步骤2: 创建游戏配置文件

在 `GameLibrary/games/my-game/game.json` 中：

```json
{
  "id": "my-game",
  "name": "我的游戏",
  "version": "1.0.0",
  "description": "游戏描述",
  "author": "作者名",
  "icon": "assets/icon.png",
  "thumbnail": "assets/thumbnail.gif",
  "tags": ["标签1", "标签2"],
  "category": "entertainment",
  "type": "iframe",
  "entry": {
    "frontend": "frontend/index.html",
    "backend": "backend/api.py"
  },
  "api": {
    "prefix": "/api/my-game",
    "endpoints": []
  },
  "websocket": {
    "enabled": false,
    "events": []
  },
  "dependencies": {
    "frontend": [],
    "backend": []
  },
  "permissions": [],
  "settings": {}
}
```

### 步骤3: 开发游戏

在 `frontend/` 目录下开发前端代码，在 `backend/` 目录下开发后端代码（可选）。

### 步骤4: 注册游戏

```python
# 扫描并注册游戏
game_manager.scan_games()
game_manager.register_game('my-game')
```

## 🎮 游戏类型

### iframe类型

游戏在独立的iframe中运行，完全隔离：

```json
{
  "type": "iframe",
  "entry": {
    "frontend": "frontend/index.html"
  }
}
```

### component类型

游戏作为组件直接集成到平台：

```json
{
  "type": "component",
  "entry": {
    "component": "MyGameComponent",
    "scripts": ["js/game.js"],
    "styles": ["css/game.css"]
  }
}
```

## 🔌 API接口

### 游戏管理API

```
GET  /api/games              # 获取所有游戏列表
GET  /api/games/:id          # 获取指定游戏信息
POST /api/games/:id/enable   # 启用游戏
POST /api/games/:id/disable  # 禁用游戏
```

### 游戏专属API

每个游戏可以定义自己的API端点，路由前缀为 `/api/games/:gameId/`

## 📡 通信机制

### 平台与游戏通信（iframe类型）

**平台发送消息给游戏：**

```javascript
gameIframe.contentWindow.postMessage({
  type: 'PLATFORM_EVENT',
  data: { userId: '123', token: 'xxx' }
}, '*');
```

**游戏发送消息给平台：**

```javascript
window.parent.postMessage({
  type: 'GAME_EVENT',
  data: { action: 'score_update', score: 100 }
}, '*');
```

### 游戏初始化消息

游戏加载时会收到初始化消息：

```javascript
window.addEventListener('message', (event) => {
  if (event.data.type === 'PLATFORM_INIT') {
    const { gameId, apiBase, token } = event.data.data;
    // 初始化游戏
  }
});
```

### 游戏就绪通知

游戏初始化完成后应发送就绪消息：

```javascript
window.parent.postMessage({
  type: 'GAME_READY',
  data: { version: '1.0.0' }
}, '*');
```

## 🛠️ 开发工具

### 游戏配置验证

```python
from GameLibrary.game_manager import game_manager

# 验证游戏配置
config = game_manager.load_game_config('my-game')
if config:
    print(f"游戏配置有效: {config['name']}")
```

### 游戏状态管理

```python
# 启用游戏
game_manager.enable_game('my-game')

# 禁用游戏
game_manager.disable_game('my-game')

# 获取游戏信息
game = game_manager.get_game('my-game')
```

## 📝 最佳实践

1. **遵循配置规范**: 确保 `game.json` 包含所有必需字段
2. **版本管理**: 使用语义化版本号
3. **错误处理**: 游戏应妥善处理错误并通知平台
4. **资源优化**: 压缩和优化游戏资源
5. **响应式设计**: 支持不同屏幕尺寸
6. **安全性**: 验证所有输入，防止XSS攻击

## 🔒 安全注意事项

1. **iframe沙箱**: iframe游戏自动运行在沙箱环境
2. **消息验证**: 验证跨窗口消息的来源
3. **API鉴权**: 所有API请求应包含有效令牌
4. **内容安全策略**: 设置适当的CSP头

## 📚 示例游戏

查看 `games/fortune-game/` 目录了解完整的游戏实现示例。

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License

## 📞 支持

如有问题或建议，请提交Issue。