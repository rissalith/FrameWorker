/**
 * 游戏加载器 - 前端
 * 负责动态加载和管理游戏模块
 */

class GameLoader {
    constructor() {
        this.games = new Map();
        this.registry = null;
        this.baseUrl = '/GameLibrary';
    }

    /**
     * 初始化游戏加载器
     */
    async init() {
        try {
            const response = await fetch(`${this.baseUrl}/game-registry.json`);
            this.registry = await response.json();
            console.log('[GameLoader] 游戏注册表加载成功', this.registry);
            return true;
        } catch (error) {
            console.error('[GameLoader] 加载游戏注册表失败:', error);
            return false;
        }
    }

    /**
     * 获取所有已注册的游戏
     */
    async getAllGames() {
        if (!this.registry) {
            await this.init();
        }
        
        const games = [];
        for (const gameInfo of this.registry.games) {
            if (gameInfo.enabled) {
                const gameConfig = await this.loadGameConfig(gameInfo.id);
                if (gameConfig) {
                    games.push({
                        ...gameInfo,
                        ...gameConfig
                    });
                }
            }
        }
        return games;
    }

    /**
     * 加载游戏配置
     */
    async loadGameConfig(gameId) {
        try {
            const gameInfo = this.registry.games.find(g => g.id === gameId);
            if (!gameInfo) {
                throw new Error(`游戏 ${gameId} 未注册`);
            }

            const response = await fetch(`${this.baseUrl}/${gameInfo.path}/game.json`);
            const config = await response.json();
            
            this.games.set(gameId, config);
            console.log(`[GameLoader] 游戏配置加载成功: ${gameId}`, config);
            return config;
        } catch (error) {
            console.error(`[GameLoader] 加载游戏配置失败: ${gameId}`, error);
            return null;
        }
    }

    /**
     * 加载游戏到指定容器
     */
    async loadGame(gameId, containerId) {
        try {
            const config = this.games.get(gameId) || await this.loadGameConfig(gameId);
            if (!config) {
                throw new Error(`无法加载游戏配置: ${gameId}`);
            }

            const container = document.getElementById(containerId);
            if (!container) {
                throw new Error(`容器不存在: ${containerId}`);
            }

            const gameInfo = this.registry.games.find(g => g.id === gameId);
            const gamePath = `${this.baseUrl}/${gameInfo.path}`;

            if (config.type === 'iframe') {
                return this.loadIframeGame(config, gamePath, container);
            } else if (config.type === 'component') {
                return this.loadComponentGame(config, gamePath, container);
            } else {
                throw new Error(`不支持的游戏类型: ${config.type}`);
            }
        } catch (error) {
            console.error(`[GameLoader] 加载游戏失败: ${gameId}`, error);
            throw error;
        }
    }

    /**
     * 加载iframe类型游戏
     */
    loadIframeGame(config, gamePath, container) {
        return new Promise((resolve, reject) => {
            // 清空容器
            container.innerHTML = '';

            // 创建iframe
            const iframe = document.createElement('iframe');
            iframe.id = `game-${config.id}`;
            iframe.src = `${gamePath}/${config.entry.frontend}`;
            iframe.style.width = '100%';
            iframe.style.height = '100%';
            iframe.style.border = 'none';
            iframe.allow = 'autoplay; fullscreen';

            // 监听加载完成
            iframe.onload = () => {
                console.log(`[GameLoader] 游戏加载完成: ${config.id}`);
                
                // 设置游戏通信
                this.setupGameCommunication(iframe, config);
                
                resolve({
                    type: 'iframe',
                    element: iframe,
                    config: config
                });
            };

            iframe.onerror = (error) => {
                console.error(`[GameLoader] 游戏加载失败: ${config.id}`, error);
                reject(error);
            };

            container.appendChild(iframe);
        });
    }

    /**
     * 加载组件类型游戏
     */
    async loadComponentGame(config, gamePath, container) {
        try {
            // 清空容器
            container.innerHTML = '';

            // 动态加载游戏脚本
            const scripts = config.entry.scripts || [];
            for (const script of scripts) {
                await this.loadScript(`${gamePath}/${script}`);
            }

            // 动态加载游戏样式
            const styles = config.entry.styles || [];
            for (const style of styles) {
                await this.loadStyle(`${gamePath}/${style}`);
            }

            // 初始化游戏组件
            if (window[config.entry.component]) {
                const GameComponent = window[config.entry.component];
                const gameInstance = new GameComponent(container, config);
                await gameInstance.init();

                console.log(`[GameLoader] 组件游戏加载完成: ${config.id}`);
                return {
                    type: 'component',
                    instance: gameInstance,
                    config: config
                };
            } else {
                throw new Error(`游戏组件未找到: ${config.entry.component}`);
            }
        } catch (error) {
            console.error(`[GameLoader] 组件游戏加载失败: ${config.id}`, error);
            throw error;
        }
    }

    /**
     * 设置游戏通信机制
     */
    setupGameCommunication(iframe, config) {
        // 监听来自游戏的消息
        window.addEventListener('message', (event) => {
            if (event.source === iframe.contentWindow) {
                this.handleGameMessage(event.data, config);
            }
        });

        // 发送初始化消息给游戏
        iframe.contentWindow.postMessage({
            type: 'PLATFORM_INIT',
            data: {
                gameId: config.id,
                apiBase: window.location.origin,
                token: this.getAuthToken()
            }
        }, '*');
    }

    /**
     * 处理来自游戏的消息
     */
    handleGameMessage(message, config) {
        console.log(`[GameLoader] 收到游戏消息:`, message);

        switch (message.type) {
            case 'GAME_READY':
                console.log(`[GameLoader] 游戏就绪: ${config.id}`);
                this.onGameReady(config, message.data);
                break;
            case 'GAME_EVENT':
                this.onGameEvent(config, message.data);
                break;
            case 'GAME_ERROR':
                console.error(`[GameLoader] 游戏错误: ${config.id}`, message.data);
                break;
            default:
                console.warn(`[GameLoader] 未知消息类型: ${message.type}`);
        }
    }

    /**
     * 游戏就绪回调
     */
    onGameReady(config, data) {
        // 触发自定义事件
        window.dispatchEvent(new CustomEvent('gameReady', {
            detail: { gameId: config.id, data }
        }));
    }

    /**
     * 游戏事件回调
     */
    onGameEvent(config, data) {
        // 触发自定义事件
        window.dispatchEvent(new CustomEvent('gameEvent', {
            detail: { gameId: config.id, data }
        }));
    }

    /**
     * 卸载游戏
     */
    unloadGame(gameId, containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = '';
            console.log(`[GameLoader] 游戏已卸载: ${gameId}`);
        }
    }

    /**
     * 动态加载脚本
     */
    loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = src;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    /**
     * 动态加载样式
     */
    loadStyle(href) {
        return new Promise((resolve, reject) => {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;
            link.onload = resolve;
            link.onerror = reject;
            document.head.appendChild(link);
        });
    }

    /**
     * 获取认证令牌
     */
    getAuthToken() {
        return localStorage.getItem('token') || '';
    }
}

// 导出单例
const gameLoader = new GameLoader();

// 如果是模块环境
if (typeof module !== 'undefined' && module.exports) {
    module.exports = gameLoader;
}

// 如果是浏览器环境
if (typeof window !== 'undefined') {
    window.GameLoader = gameLoader;
}