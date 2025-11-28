# 游戏库集成指南

本文档说明如何将游戏库集成到XMGamer平台中。

## 后端集成

### 1. 导入游戏管理器

在 `XMGamer/backend/app.py` 中添加：

```python
import sys
from pathlib import Path

# 添加GameLibrary到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 导入游戏管理器
from GameLibrary.game_manager import game_manager

# 初始化游戏管理器
game_manager.init()

# 注册游戏API蓝图
game_api_bp = game_manager.create_api_blueprint()
app.register_blueprint(game_api_bp)
```

### 2. 配置静态文件服务

确保Flask能够访问GameLibrary目录：

```python
# 在路由中添加GameLibrary静态文件支持
@app.route('/GameLibrary/<path:path>')
def serve_game_library(path):
    return send_from_directory('../GameLibrary', path)
```

### 3. 游戏API端点

游戏管理器会自动注册以下API端点：

- `GET /api/games` - 获取所有游戏列表
- `GET /api/games/:id` - 获取指定游戏信息
- `POST /api/games/:id/enable` - 启用游戏
- `POST /api/games/:id/disable` - 禁用游戏

## 前端集成

### 1. 引入游戏加载器

在主HTML文件中添加：

```html
<!-- 引入游戏加载器 -->
<script src="/GameLibrary/game-loader.js"></script>
```

### 2. 初始化游戏加载器

在应用初始化时：

```javascript
// 初始化游戏加载器
async function initGameLibrary() {
    const success = await GameLoader.init();
    if (success) {
        console.log('游戏库初始化成功');
        await loadGameMarket();
    } else {
        console.error('游戏库初始化失败');
    }
}

// 加载游戏市场
async function loadGameMarket() {
    const games = await GameLoader.getAllGames();
    renderGameCards(games);
}
```

### 3. 渲染游戏卡片

```javascript
function renderGameCards(games) {
    const container = document.querySelector('.games-grid');
    container.innerHTML = '';
    
    games.forEach(game => {
        const card = createGameCard(game);
        container.appendChild(card);
    });
}

function createGameCard(game) {
    const card = document.createElement('div');
    card.className = 'game-card';
    card.dataset.gameId = game.id;
    
    card.innerHTML = `
        <div class="game-card-image">
            <img src="/GameLibrary/${game.path}/${game.thumbnail}" alt="${game.name}">
        </div>
        <div class="game-card-content">
            <h4 class="game-title">${game.name}</h4>
            <p class="game-description">${game.description}</p>
            <div class="game-tags">
                ${game.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
            </div>
        </div>
        <div class="game-card-footer">
            <button class="btn-play" onclick="launchGame('${game.id}')">开始游戏</button>
        </div>
    `;
    
    return card;
}
```

### 4. 启动游戏

```javascript
async function launchGame(gameId) {
    try {
        // 创建游戏容器
        const container = document.getElementById('game-container');
        container.innerHTML = '<div id="game-iframe-container"></div>';
        
        // 加载游戏
        await GameLoader.loadGame(gameId, 'game-iframe-container');
        
        // 显示游戏容器
        container.style.display = 'block';
        
        console.log(`游戏 ${gameId} 启动成功`);
    } catch (error) {
        console.error(`启动游戏失败: ${gameId}`, error);
        alert('游戏启动失败，请稍后重试');
    }
}
```

### 5. 监听游戏事件

```javascript
// 监听游戏就绪事件
window.addEventListener('gameReady', (event) => {
    const { gameId, data } = event.detail;
    console.log(`游戏就绪: ${gameId}`, data);
});

// 监听游戏事件
window.addEventListener('gameEvent', (event) => {
    const { gameId, data } = event.detail;
    console.log(`游戏事件: ${gameId}`, data);
    
    // 处理游戏事件
    handleGameEvent(gameId, data);
});

function handleGameEvent(gameId, data) {
    switch (data.action) {
        case 'score_update':
            updateScore(data.score);
            break;
        case 'game_over':
            handleGameOver(data);
            break;
        // 添加更多事件处理
    }
}
```

## 游戏市场页面更新

### 修改 `frontend/pages/game-market.html`

```html
<div class="page-content" id="game-market-page">
    <div class="game-market-container">
        <div class="games-container">
            <div class="market-toolbar">
                <div class="view-mode-toggle">
                    <button class="view-btn active" data-view="card">卡片视图</button>
                    <button class="view-btn" data-view="list">列表视图</button>
                </div>
            </div>
            
            <!-- 游戏网格容器 - 将由JavaScript动态填充 -->
            <div class="games-grid" data-view-mode="card" id="games-grid">
                <div class="loading">加载游戏中...</div>
            </div>
        </div>
    </div>
</div>
```

### 更新路由处理

在 `frontend/js/modules/router.js` 中：

```javascript
const routes = {
    'game-market': {
        title: '游戏市场',
        load: async () => {
            await loadPage('pages/game-market.html', 'game-market-page');
            // 加载游戏列表
            await loadGameMarket();
        }
    },
    // 其他路由...
};

async function loadGameMarket() {
    const games = await GameLoader.getAllGames();
    const container = document.getElementById('games-grid');
    
    if (games.length === 0) {
        container.innerHTML = '<div class="no-games">暂无可用游戏</div>';
        return;
    }
    
    container.innerHTML = '';
    games.forEach(game => {
        const card = createGameCard(game);
        container.appendChild(card);
    });
}
```

## 游戏通信示例

### 平台发送消息给游戏

```javascript
function sendMessageToGame(gameId, message) {
    const iframe = document.querySelector(`#game-${gameId}`);
    if (iframe && iframe.contentWindow) {
        iframe.contentWindow.postMessage({
            type: 'PLATFORM_EVENT',
            data: message
        }, '*');
    }
}

// 示例：发送用户信息给游戏
sendMessageToGame('fortune-game', {
    userId: currentUser.id,
    username: currentUser.name,
    token: authToken
});
```

### 游戏内接收平台消息

在游戏的JavaScript中：

```javascript
window.addEventListener('message', (event) => {
    if (event.data.type === 'PLATFORM_INIT') {
        const { gameId, apiBase, token } = event.data.data;
        // 初始化游戏
        initGame(gameId, apiBase, token);
    } else if (event.data.type === 'PLATFORM_EVENT') {
        // 处理平台事件
        handlePlatformEvent(event.data.data);
    }
});

// 游戏向平台发送消息
function sendToPlatform(type, data) {
    window.parent.postMessage({
        type: type,
        data: data
    }, '*');
}

// 通知平台游戏已就绪
sendToPlatform('GAME_READY', {
    version: '1.0.0',
    features: ['multiplayer', 'leaderboard']
});
```

## 测试集成

### 1. 测试后端

```bash
cd XMGamer/backend
python app.py
```

访问 `http://localhost:3000/api/games` 应该返回游戏列表。

### 2. 测试前端

在浏览器控制台中：

```javascript
// 测试游戏加载器
await GameLoader.init();
const games = await GameLoader.getAllGames();
console.log('可用游戏:', games);

// 测试加载游戏
await GameLoader.loadGame('fortune-game', 'game-container');
```

### 3. 测试游戏通信

在游戏iframe中打开控制台，应该能看到：
- `PLATFORM_INIT` 消息
- 游戏配置信息
- API基础URL和令牌

## 故障排除

### 问题1: 游戏列表为空

**原因**: 游戏注册表未正确加载或游戏未启用

**解决方案**:
1. 检查 `GameLibrary/game-registry.json` 是否存在
2. 确认游戏的 `enabled` 字段为 `true`
3. 检查后端日志中的游戏库初始化信息

### 问题2: 游戏无法加载

**原因**: 路径配置错误或CORS问题

**解决方案**:
1. 检查游戏配置文件中的路径
2. 确认Flask配置了正确的静态文件路由
3. 检查浏览器控制台的CORS错误

### 问题3: 游戏通信失败

**原因**: postMessage配置错误或消息格式不匹配

**解决方案**:
1. 检查消息格式是否符合规范
2. 确认iframe的origin设置正确
3. 在两端添加日志输出调试消息流

## 最佳实践

1. **错误处理**: 始终添加try-catch处理游戏加载错误
2. **加载状态**: 显示加载指示器提升用户体验
3. **资源清理**: 卸载游戏时清理事件监听器
4. **安全性**: 验证postMessage的来源
5. **性能**: 使用懒加载避免一次性加载所有游戏

## 下一步

1. 添加更多游戏到游戏库
2. 实现游戏评分和评论系统
3. 添加游戏数据分析
4. 支持游戏热更新
5. 实现游戏市场搜索和筛选

## 参考资料

- [游戏库架构文档](ARCHITECTURE.md)
- [游戏库使用说明](README.md)
- [巫女占卜游戏示例](games/fortune-game/README.md)