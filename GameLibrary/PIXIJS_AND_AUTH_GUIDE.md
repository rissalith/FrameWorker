# Pixi.js集成与游戏访问控制指南

## 概述

本文档说明如何在游戏库中集成Pixi.js，以及如何实现游戏访问控制，确保游戏只能通过平台登录后访问。

## 一、Pixi.js集成方案

### 1. Component类型游戏（推荐）

使用component类型可以让Pixi.js游戏直接嵌入平台，无需iframe隔离，性能更好。

#### 游戏配置示例

```json
{
  "id": "pixi-game",
  "name": "Pixi.js游戏示例",
  "version": "1.0.0",
  "type": "component",
  "entry": {
    "component": "PixiGame",
    "scripts": [
      "https://cdn.jsdelivr.net/npm/pixi.js@7.3.2/dist/pixi.min.js",
      "js/game.js"
    ],
    "styles": [
      "css/game.css"
    ]
  },
  "dependencies": {
    "frontend": [
      "pixi.js@7.3.2"
    ]
  }
}
```

#### 游戏实现示例

```javascript
// GameLibrary/games/pixi-game/frontend/js/game.js

class PixiGame {
    constructor(container, config) {
        this.container = container;
        this.config = config;
        this.app = null;
        this.authToken = null;
        this.userId = null;
    }

    async init() {
        // 等待平台初始化消息
        await this.waitForPlatformInit();
        
        // 验证用户登录状态
        if (!await this.verifyAuth()) {
            this.showLoginRequired();
            return;
        }

        // 创建Pixi应用
        this.app = new PIXI.Application({
            width: this.container.clientWidth,
            height: this.container.clientHeight,
            backgroundColor: 0x1099bb,
            resolution: window.devicePixelRatio || 1,
        });

        this.container.appendChild(this.app.view);

        // 初始化游戏
        await this.loadAssets();
        this.setupGame();
        this.startGameLoop();

        // 通知平台游戏已就绪
        this.notifyPlatform('GAME_READY', {
            version: this.config.version
        });
    }

    async waitForPlatformInit() {
        return new Promise((resolve) => {
            window.addEventListener('message', (event) => {
                if (event.data.type === 'PLATFORM_INIT') {
                    this.authToken = event.data.data.token;
                    this.userId = event.data.data.userId;
                    this.apiBase = event.data.data.apiBase;
                    resolve();
                }
            });
        });
    }

    async verifyAuth() {
        if (!this.authToken) {
            return false;
        }

        try {
            const response = await fetch(`${this.apiBase}/api/auth/verify`, {
                headers: {
                    'Authorization': `Bearer ${this.authToken}`
                }
            });
            return response.ok;
        } catch (error) {
            console.error('认证验证失败:', error);
            return false;
        }
    }

    showLoginRequired() {
        this.container.innerHTML = `
            <div class="login-required">
                <h2>需要登录</h2>
                <p>请先登录平台才能开始游戏</p>
                <button onclick="window.parent.postMessage({type: 'GAME_EVENT', data: {action: 'request_login'}}, '*')">
                    前往登录
                </button>
            </div>
        `;
    }

    async loadAssets() {
        // 加载游戏资源
        await PIXI.Assets.load([
            'assets/sprite.png',
            'assets/background.png'
        ]);
    }

    setupGame() {
        // 创建游戏场景
        const sprite = PIXI.Sprite.from('assets/sprite.png');
        sprite.anchor.set(0.5);
        sprite.x = this.app.screen.width / 2;
        sprite.y = this.app.screen.height / 2;
        this.app.stage.addChild(sprite);

        // 添加交互
        sprite.eventMode = 'static';
        sprite.cursor = 'pointer';
        sprite.on('pointerdown', () => {
            this.notifyPlatform('GAME_EVENT', {
                action: 'sprite_clicked',
                userId: this.userId
            });
        });
    }

    startGameLoop() {
        this.app.ticker.add((delta) => {
            // 游戏循环逻辑
        });
    }

    notifyPlatform(type, data) {
        window.parent.postMessage({
            type: type,
            data: data
        }, '*');
    }

    destroy() {
        if (this.app) {
            this.app.destroy(true);
        }
    }
}

// 导出到全局
window.PixiGame = PixiGame;
```

### 2. iframe类型游戏（隔离性更好）

如果需要更强的隔离性，可以使用iframe类型。

#### 游戏HTML示例

```html
<!-- GameLibrary/games/pixi-game/frontend/index.html -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>Pixi.js游戏</title>
    <script src="https://cdn.jsdelivr.net/npm/pixi.js@7.3.2/dist/pixi.min.js"></script>
    <style>
        body { margin: 0; padding: 0; overflow: hidden; }
        #game-container { width: 100vw; height: 100vh; }
        .auth-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            z-index: 1000;
        }
    </style>
</head>
<body>
    <div id="game-container"></div>
    <div id="auth-overlay" class="auth-overlay" style="display: none;">
        <div>
            <h2>需要登录</h2>
            <p>请通过平台登录后访问游戏</p>
        </div>
    </div>

    <script>
        let app = null;
        let authToken = null;
        let userId = null;
        let apiBase = null;

        // 监听平台初始化消息
        window.addEventListener('message', async (event) => {
            if (event.data.type === 'PLATFORM_INIT') {
                authToken = event.data.data.token;
                userId = event.data.data.userId;
                apiBase = event.data.data.apiBase;

                // 验证认证
                if (await verifyAuth()) {
                    initGame();
                } else {
                    showAuthRequired();
                }
            }
        });

        async function verifyAuth() {
            if (!authToken) return false;

            try {
                const response = await fetch(`${apiBase}/api/auth/verify`, {
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    }
                });
                return response.ok;
            } catch (error) {
                console.error('认证失败:', error);
                return false;
            }
        }

        function showAuthRequired() {
            document.getElementById('auth-overlay').style.display = 'flex';
        }

        async function initGame() {
            // 创建Pixi应用
            app = new PIXI.Application({
                width: window.innerWidth,
                height: window.innerHeight,
                backgroundColor: 0x1099bb,
            });

            document.getElementById('game-container').appendChild(app.view);

            // 加载资源并初始化游戏
            await loadAssets();
            setupGame();

            // 通知平台游戏已就绪
            window.parent.postMessage({
                type: 'GAME_READY',
                data: { version: '1.0.0', userId: userId }
            }, '*');
        }

        async function loadAssets() {
            // 加载游戏资源
        }

        function setupGame() {
            // 设置游戏场景
        }

        // 窗口大小调整
        window.addEventListener('resize', () => {
            if (app) {
                app.renderer.resize(window.innerWidth, window.innerHeight);
            }
        });
    </script>
</body>
</html>
```

## 二、游戏访问控制机制

### 1. 后端认证中间件

在后端添加游戏访问验证：

```python
# GameLibrary/game-auth.py

from functools import wraps
from flask import request, jsonify
import jwt

def verify_game_access(f):
    """游戏访问验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({
                'success': False,
                'message': '未提供认证令牌'
            }), 401
        
        try:
            # 验证JWT令牌
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            request.user_id = payload.get('user_id')
            request.username = payload.get('username')
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': '令牌已过期'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': '无效的令牌'
            }), 401
    
    return decorated_function

# 在app.py中添加验证端点
@app.route('/api/auth/verify', methods=['GET'])
@verify_game_access
def verify_auth():
    """验证用户认证状态"""
    return jsonify({
        'success': True,
        'user_id': request.user_id,
        'username': request.username
    })
```

### 2. 游戏加载器增强

更新游戏加载器以传递认证信息：

```javascript
// GameLibrary/game-loader.js (增强版)

class GameLoader {
    // ... 现有代码 ...

    setupGameCommunication(iframe, config) {
        // 监听来自游戏的消息
        window.addEventListener('message', (event) => {
            if (event.source === iframe.contentWindow) {
                this.handleGameMessage(event.data, config);
            }
        });

        // 获取用户信息和令牌
        const userInfo = this.getUserInfo();
        const token = this.getAuthToken();

        // 发送初始化消息给游戏
        iframe.contentWindow.postMessage({
            type: 'PLATFORM_INIT',
            data: {
                gameId: config.id,
                apiBase: window.location.origin,
                token: token,
                userId: userInfo.id,
                username: userInfo.username,
                timestamp: Date.now()
            }
        }, '*');
    }

    getUserInfo() {
        // 从localStorage或其他地方获取用户信息
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : { id: null, username: 'Guest' };
    }

    getAuthToken() {
        return localStorage.getItem('token') || '';
    }

    handleGameMessage(message, config) {
        console.log(`[GameLoader] 收到游戏消息:`, message);

        switch (message.type) {
            case 'GAME_READY':
                console.log(`[GameLoader] 游戏就绪: ${config.id}`);
                this.onGameReady(config, message.data);
                break;
            case 'GAME_EVENT':
                if (message.data.action === 'request_login') {
                    // 游戏请求登录
                    this.redirectToLogin();
                } else {
                    this.onGameEvent(config, message.data);
                }
                break;
            case 'GAME_ERROR':
                console.error(`[GameLoader] 游戏错误: ${config.id}`, message.data);
                break;
            default:
                console.warn(`[GameLoader] 未知消息类型: ${message.type}`);
        }
    }

    redirectToLogin() {
        // 重定向到登录页面
        window.location.href = '/login.html?redirect=' + encodeURIComponent(window.location.pathname);
    }
}
```

### 3. 平台路由保护

在前端路由中添加认证检查：

```javascript
// XMGamer/frontend/js/modules/router.js (增强版)

const routes = {
    'game-market': {
        title: '游戏市场',
        requireAuth: true,  // 需要认证
        load: async () => {
            // 检查认证状态
            if (!await checkAuth()) {
                redirectToLogin();
                return;
            }
            
            await loadPage('pages/game-market.html', 'game-market-page');
            await loadGameMarket();
        }
    },
    // 其他路由...
};

async function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) return false;

    try {
        const response = await fetch('/api/auth/verify', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        return response.ok;
    } catch (error) {
        console.error('认证检查失败:', error);
        return false;
    }
}

function redirectToLogin() {
    const currentPath = window.location.hash.substring(1);
    window.location.href = `/login.html?redirect=${encodeURIComponent(currentPath)}`;
}
```

## 三、完整的游戏示例

### Pixi.js游戏配置

```json
{
  "id": "pixi-adventure",
  "name": "Pixi冒险游戏",
  "version": "1.0.0",
  "description": "基于Pixi.js的冒险游戏",
  "type": "component",
  "entry": {
    "component": "PixiAdventure",
    "scripts": [
      "https://cdn.jsdelivr.net/npm/pixi.js@7.3.2/dist/pixi.min.js",
      "js/game.js"
    ],
    "styles": [
      "css/game.css"
    ]
  },
  "dependencies": {
    "frontend": [
      "pixi.js@7.3.2"
    ]
  },
  "permissions": [
    "api",
    "user-data"
  ],
  "requireAuth": true
}
```

## 四、安全最佳实践

### 1. 令牌管理
- 使用JWT令牌进行认证
- 令牌设置合理的过期时间
- 定期刷新令牌

### 2. 访问控制
- 游戏URL不应直接暴露
- 所有游戏请求必须携带有效令牌
- 后端验证每个游戏API请求

### 3. 数据保护
- 敏感数据加密传输
- 游戏数据与用户ID绑定
- 实施CORS策略

### 4. 防止直接访问
```python
# 在后端添加游戏资源访问控制
@app.route('/GameLibrary/games/<game_id>/<path:path>')
@verify_game_access
def serve_game_resource(game_id, path):
    """提供游戏资源，需要认证"""
    game_path = Path('GameLibrary/games') / game_id / path
    if game_path.exists():
        return send_file(game_path)
    return jsonify({'error': '资源不存在'}), 404
```

## 五、使用流程

### 用户访问游戏的完整流程

1. **用户登录平台** → 获得JWT令牌
2. **浏览游戏市场** → 查看可用游戏
3. **点击游戏** → GameLoader加载游戏
4. **传递令牌** → 平台向游戏发送PLATFORM_INIT消息（包含令牌）
5. **游戏验证** → 游戏调用/api/auth/verify验证令牌
6. **验证成功** → 游戏初始化并开始
7. **验证失败** → 显示登录提示

### 防止直接访问

- 游戏HTML文件检查PLATFORM_INIT消息
- 没有收到消息或令牌无效时显示登录提示
- 所有游戏API调用都需要携带令牌

## 六、总结

通过以上方案，您可以：

✅ **集成Pixi.js**: 支持component和iframe两种方式
✅ **访问控制**: 游戏只能通过平台登录后访问
✅ **即开即用**: 用户登录后可立即开始游戏
✅ **安全可靠**: JWT令牌验证，防止未授权访问
✅ **灵活扩展**: 易于添加新的Pixi.js游戏

这个方案既保证了游戏的安全性，又提供了良好的用户体验！