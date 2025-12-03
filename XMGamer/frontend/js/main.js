/**
 * 主入口文件
 * XMGamer - 直播互动游戏平台
 */

const App = {
    /**
     * 初始化应用
     */
    init() {
        console.log('XMGamer 正在初始化...');
        
        // 初始化认证管理器
        AuthManager.init();
        
        // 检查登录状态
        if (!AuthManager.isLoggedIn()) {
            // 未登录，跳转到登录页
            window.location.href = '/login.html';
            return;
        }
        
        // 初始化路由系统
        Router.init();
        
        // 更新用户信息显示
        this._updateUserDisplay();
        
        // 绑定用户菜单事件
        this._bindUserMenuEvents();
        
        // 监听认证状态变化
        this._bindAuthEvents();
        
        // 初始化游戏市场视图切换
        this._initGameMarketView();
        
        // 初始化游戏市场模块
        if (window.GameMarket) {
            GameMarket.init();
        }
        
        console.log('XMGamer 已加载 ✅');
        console.log('欢迎来到直播互动游戏平台！');
    },
    
    /**
     * 初始化游戏市场视图切换功能
     * @private
     */
    _initGameMarketView() {
        const viewButtons = document.querySelectorAll('.view-btn');
        const gamesGrid = document.querySelector('.games-grid');
        
        if (!viewButtons.length || !gamesGrid) return;
        
        viewButtons.forEach(btn => {
            btn.addEventListener('click', () => {
                const viewMode = btn.dataset.view;
                
                // 更新按钮状态
                viewButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                
                // 更新视图模式
                gamesGrid.dataset.viewMode = viewMode;
                
                // 保存用户偏好
                localStorage.setItem('gameMarketViewMode', viewMode);
            });
        });
        
        // 恢复用户上次选择的视图模式
        const savedViewMode = localStorage.getItem('gameMarketViewMode');
        if (savedViewMode) {
            const targetBtn = document.querySelector(`.view-btn[data-view="${savedViewMode}"]`);
            if (targetBtn) {
                targetBtn.click();
            }
        }
    },

    /**
     * 绑定用户菜单事件
     * @private
     */
    _bindUserMenuEvents() {
        const userProfile = document.getElementById('userProfile');
        const userMenu = document.getElementById('userMenu');
        
        if (userProfile && userMenu) {
            // 切换菜单显示
            userProfile.addEventListener('click', (e) => {
                e.stopPropagation();
                const isVisible = userMenu.style.display === 'block';
                userMenu.style.display = isVisible ? 'none' : 'block';
            });
            
            // 点击其他地方关闭菜单
            document.addEventListener('click', () => {
                userMenu.style.display = 'none';
            });
            
            // 菜单选项点击事件
            userMenu.querySelectorAll('.menu-option').forEach(option => {
                option.addEventListener('click', (e) => {
                    e.stopPropagation();
                    const action = option.dataset.action;
                    this._handleMenuAction(action);
                    userMenu.style.display = 'none';
                });
            });
        }
    },
    
    /**
     * 处理菜单操作
     * @private
     */
    _handleMenuAction(action) {
        switch (action) {
            case 'settings':
                // 导航到设置页面
                if (window.Router) {
                    Router.navigate('settings');
                }
                break;
            case 'wallet':
                const walletMsg = window.I18n ? I18n.t('wallet_coming_soon') : '钱包功能即将推出';
                alert(walletMsg);
                break;
            case 'logout':
                const logoutMsg = window.I18n ? I18n.t('logout_confirm') : '确定要退出登录吗？';
                if (confirm(logoutMsg)) {
                    AuthManager.logout();
                }
                break;
        }
    },
    
    /**
     * 更新用户信息显示
     * @private
     */
    _updateUserDisplay() {
        const user = AuthManager.getCurrentUser();
        if (!user) return;
        
        const userNameEl = document.querySelector('.user-name');
        if (userNameEl) {
            userNameEl.textContent = user.nickname || user.phone || '游戏玩家';
        }
    },
    
    /**
     * 绑定认证相关事件
     * @private
     */
    _bindAuthEvents() {
        // 监听用户信息更新
        window.addEventListener('userInfoUpdated', (e) => {
            this._updateUserDisplay();
        });
        
        // 监听认证状态变化
        window.addEventListener('authStateChanged', (e) => {
            if (!e.detail.isAuthenticated) {
                // 已退出登录，跳转到登录页
                window.location.href = '/login.html';
            }
        });
    }
};

// 当DOM加载完成后初始化应用
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => App.init());
} else {
    App.init();
}

// 导出App对象供调试使用
window.App = App;