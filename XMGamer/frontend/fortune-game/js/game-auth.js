/**
 * 游戏端授权验证模块
 * 用于验证平台提供的游戏Token
 */

class GameAuth {
    constructor() {
        this.platformUrl = window.location.origin;
        this.ticket = null;
        this.userData = null;
        this.isValid = false;
    }

    /**
     * 初始化并验证Token
     */
    async init() {
        console.log('[GameAuth] 初始化游戏授权验证...');
        
        // 从URL获取ticket
        this.ticket = this.getTicketFromUrl();
        
        if (!this.ticket) {
            console.error('[GameAuth] 未找到授权票据');
            return {
                success: false,
                error: '未找到授权票据，请从平台启动游戏'
            };
        }
        
        // 验证ticket
        const result = await this.verifyTicket();
        
        if (result.success) {
            console.log('[GameAuth] 授权验证成功', result.data);
            this.isValid = true;
            this.userData = result.data;
            
            // 保存用户信息到localStorage（可选）
            this.saveUserData();
            
            return {
                success: true,
                data: result.data
            };
        } else {
            console.error('[GameAuth] 授权验证失败:', result.error);
            return {
                success: false,
                error: result.error
            };
        }
    }

    /**
     * 从URL获取ticket参数
     */
    getTicketFromUrl() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('ticket');
    }

    /**
     * 验证ticket
     */
    async verifyTicket() {
        try {
            const response = await fetch(
                `${this.platformUrl}/api/games/verify?ticket=${this.ticket}`,
                {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                }
            );

            const data = await response.json();

            if (!response.ok) {
                return {
                    success: false,
                    error: data.error || '验证失败'
                };
            }

            if (!data.valid) {
                return {
                    success: false,
                    error: data.error || 'Token无效'
                };
            }

            return {
                success: true,
                data: {
                    userId: data.user_id,
                    gameId: data.game_id,
                    plan: data.plan,
                    nickname: data.nickname,
                    avatarUrl: data.avatar_url,
                    expiresAt: data.expires_at
                }
            };

        } catch (error) {
            console.error('[GameAuth] 验证请求失败:', error);
            return {
                success: false,
                error: '网络错误，请检查连接'
            };
        }
    }

    /**
     * 保存用户数据到localStorage
     */
    saveUserData() {
        if (this.userData) {
            try {
                localStorage.setItem('game_user_data', JSON.stringify(this.userData));
                console.log('[GameAuth] 用户数据已保存');
            } catch (error) {
                console.error('[GameAuth] 保存用户数据失败:', error);
            }
        }
    }

    /**
     * 从localStorage读取用户数据
     */
    loadUserData() {
        try {
            const data = localStorage.getItem('game_user_data');
            if (data) {
                this.userData = JSON.parse(data);
                return this.userData;
            }
        } catch (error) {
            console.error('[GameAuth] 读取用户数据失败:', error);
        }
        return null;
    }

    /**
     * 获取用户信息
     */
    getUserData() {
        return this.userData;
    }

    /**
     * 检查授权是否有效
     */
    isAuthorized() {
        return this.isValid && this.userData !== null;
    }

    /**
     * 获取用户计划等级
     */
    getUserPlan() {
        return this.userData?.plan || 'free';
    }

    /**
     * 检查是否为Pro用户
     */
    isProUser() {
        const plan = this.getUserPlan();
        return plan === 'pro' || plan === 'premium';
    }

    /**
     * 显示授权错误页面
     */
    showAuthError(message) {
        document.body.innerHTML = `
            <div style="
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                padding: 20px;
            ">
                <div style="
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    border-radius: 20px;
                    padding: 40px;
                    max-width: 500px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                ">
                    <h1 style="font-size: 48px; margin: 0 0 20px 0;">🔒</h1>
                    <h2 style="margin: 0 0 10px 0;">授权验证失败</h2>
                    <p style="margin: 0 0 30px 0; opacity: 0.9;">${message}</p>
                    <button onclick="window.location.href='${this.platformUrl}/home.html'" style="
                        background: white;
                        color: #667eea;
                        border: none;
                        padding: 12px 30px;
                        border-radius: 25px;
                        font-size: 16px;
                        font-weight: bold;
                        cursor: pointer;
                        transition: transform 0.2s;
                    " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
                        返回平台
                    </button>
                </div>
            </div>
        `;
    }
}

// 导出单例
const gameAuth = new GameAuth();

// 浏览器环境
if (typeof window !== 'undefined') {
    window.GameAuth = gameAuth;
}

// 模块环境
if (typeof module !== 'undefined' && module.exports) {
    module.exports = gameAuth;
}