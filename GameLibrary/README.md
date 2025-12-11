# MaxGamer 游戏库

MaxGamer平台的游戏库，按平台组织游戏内容。

## 📁 目录结构

```
GameLibrary/
├── douyin/              # 抖音平台游戏
│   └── fortune-game/    # 巫女上上签游戏
│       ├── backend/     # Python Flask后端
│       └── frontend/    # PixiJS前端
├── tiktok/              # TikTok平台游戏
│   └── fortune-game/    # 巫女上上签游戏
│       ├── backend/
│       └── frontend/
└── twitch/              # Twitch平台游戏
    └── fortune-game-twitch/  # 巫女上上签游戏（Twitch版）
        ├── backend/
        └── frontend/
```

## 🎮 游戏列表

### 巫女上上签 (Miko Fortune)
- **游戏ID**: fortune-game
- **支持平台**: 抖音 / TikTok / Twitch
- **类型**: AI互动占卜游戏
- **技术栈**:
  - 前端: PixiJS, HTML5, CSS3
  - 后端: Python Flask
  - AI: DeepSeek API / LLMX
  - 实时通信: WebSocket

## 🔗 相关仓库

- [Fortune-Game独立仓库](https://github.com/rissalith/Fortune-Game) - 游戏专用仓库
- [MaxGamer平台](https://github.com/WistonPeng/Max-Gamer-Platform) - 平台主仓库
- [FrameWorker](https://github.com/rissalith/MaxGamer) - 框架仓库

## 🚀 游戏管理

- `game-registry.json` - 游戏注册配置
- `game_manager.py` - 游戏加载管理器
- `game_session_manager.py` - 游戏会话管理
- `game-loader.js` - 前端游戏加载器

## 📜 许可证

MIT License
