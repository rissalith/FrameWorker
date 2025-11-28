/**
 * 游戏市场模块
 * 处理游戏启动、授权等功能
 */

const GameMarket = {
    /**
     * 初始化游戏市场
     */
    init() {
        console.log('[GameMarket] 初始化游戏市场...');
        this.bindEvents();
        console.log('[GameMarket] 游戏市场已初始化 ✅');
    },

    /**
     * 绑定事件
     */
    bindEvents() {
        // 绑定所有"开始游戏"按钮
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-play') && !e.target.disabled) {
                const gameCard = e.target.closest('.game-card');
                if (gameCard && !gameCard.classList.contains('coming-soon')) {
                    const gameId = gameCard.dataset.game;
                    this.launchGame(gameId);
                }
            }
        });

        // 视图切换
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.switchView(btn.dataset.view);
            });
        });
    },

    /**
     * 启动游戏
     */
    async launchGame(gameId) {
        console.log(`[GameMarket] 启动游戏: ${gameId}`);

        // 检查登录状态
        if (!window.AuthManager || !window.AuthManager.isLoggedIn()) {
            this.showMessage('请先登录', 'warning');
            // 跳转到登录页
            setTimeout(() => {
                window.location.href = '/index.html';
            }, 1500);
            return;
        }

        try {
            // 显示加载状态
            this.showMessage('正在启动游戏...', 'info');

            // 调用启动API
            const response = await window.AuthManager.authenticatedFetch('/api/games/launch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ game_id: gameId })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || '启动游戏失败');
            }

            console.log('[GameMarket] 游戏启动成功:', data);

            // 显示成功消息
            this.showMessage('游戏启动成功！', 'success');

            // 跳转到游戏
            setTimeout(() => {
                window.location.href = data.launch_url;
            }, 500);

        } catch (error) {
            console.error('[GameMarket] 启动游戏失败:', error);
            this.showMessage(error.message || '启动游戏失败', 'error');
        }
    },

    /**
     * 切换视图模式
     */
    switchView(viewMode) {
        const gamesGrid = document.querySelector('.games-grid');
        const viewBtns = document.querySelectorAll('.view-btn');

        if (gamesGrid) {
            gamesGrid.dataset.viewMode = viewMode;
        }

        viewBtns.forEach(btn => {
            if (btn.dataset.view === viewMode) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        });
    },

    /**
     * 显示消息提示
     */
    showMessage(message, type = 'info') {
        // 移除已存在的消息
        const existingMsg = document.querySelector('.game-market-message');
        if (existingMsg) {
            existingMsg.remove();
        }

        // 创建消息元素
        const messageEl = document.createElement('div');
        messageEl.className = `game-market-message ${type}`;
        messageEl.textContent = message;

        // 添加样式
        Object.assign(messageEl.style, {
            position: 'fixed',
            top: '20px',
            left: '50%',
            transform: 'translateX(-50%)',
            padding: '12px 24px',
            borderRadius: '8px',
            color: 'white',
            fontSize: '14px',
            fontWeight: '500',
            zIndex: '10000',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            animation: 'slideDown 0.3s ease-out'
        });

        // 根据类型设置背景色
        const colors = {
            info: '#3498db',
            success: '#2ecc71',
            warning: '#f39c12',
            error: '#e74c3c'
        };
        messageEl.style.background = colors[type] || colors.info;

        // 添加到页面
        document.body.appendChild(messageEl);

        // 3秒后自动移除
        setTimeout(() => {
            messageEl.style.animation = 'slideUp 0.3s ease-out';
            setTimeout(() => {
                messageEl.remove();
            }, 300);
        }, 3000);
    },

    /**
     * 获取用户的游戏授权列表
     */
    async getUserLicenses() {
        try {
            const response = await window.AuthManager.authenticatedFetch('/api/games/licenses');
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || '获取授权列表失败');
            }

            return data.licenses || [];
        } catch (error) {
            console.error('[GameMarket] 获取授权列表失败:', error);
            return [];
        }
    },

    /**
     * 获取游戏启动历史
     */
    async getLaunchHistory(limit = 10) {
        try {
            const response = await window.AuthManager.authenticatedFetch(
                `/api/games/history?limit=${limit}`
            );
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.message || '获取历史记录失败');
            }

            return data.history || [];
        } catch (error) {
            console.error('[GameMarket] 获取历史记录失败:', error);
            return [];
        }
    }
};

// 添加CSS动画
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateX(-50%) translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
    }

    @keyframes slideUp {
        from {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
        to {
            opacity: 0;
            transform: translateX(-50%) translateY(-20px);
        }
    }
`;
document.head.appendChild(style);

// 导出模块
window.GameMarket = GameMarket;