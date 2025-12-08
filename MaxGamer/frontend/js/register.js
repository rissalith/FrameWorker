/**
 * 注册页面脚本
 * 处理注册表单交互和验证
 */

const RegisterPage = {
    // DOM元素
    elements: {},
    
    // 倒计时相关
    countdown: 0,
    countdownTimer: null,
    
    /**
     * 初始化注册页面
     */
    init() {
        console.log('注册页面初始化...');
        
        // 初始化认证管理器
        AuthManager.init();
        
        // 检查是否已登录
        if (AuthManager.isLoggedIn()) {
            // 已登录，跳转到主页
            window.location.href = '/index.html';
            return;
        }
        
        // 缓存DOM元素
        this._cacheElements();
        
        // 绑定事件
        this._bindEvents();
        
        console.log('注册页面已初始化 ✅');
    },
    
    /**
     * 缓存DOM元素
     * @private
     */
    _cacheElements() {
        this.elements = {
            registerForm: document.getElementById('registerForm'),
            emailInput: document.getElementById('emailInput'),
            codeInput: document.getElementById('codeInput'),
            passwordInput: document.getElementById('passwordInput'),
            confirmPasswordInput: document.getElementById('confirmPasswordInput'),
            nicknameInput: document.getElementById('nicknameInput'),
            sendCodeBtn: document.getElementById('sendCodeBtn'),
            registerBtn: document.getElementById('registerBtn'),
            emailError: document.getElementById('emailError'),
            codeError: document.getElementById('codeError'),
            passwordError: document.getElementById('passwordError'),
            confirmPasswordError: document.getElementById('confirmPasswordError'),
            nicknameError: document.getElementById('nicknameError'),
            authStatus: document.getElementById('authStatus')
        };
    },
    
    /**
     * 绑定事件
     * @private
     */
    _bindEvents() {
        const {
            registerForm, sendCodeBtn, emailInput, codeInput,
            passwordInput, confirmPasswordInput, nicknameInput
        } = this.elements;
        
        // 表单提交
        registerForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleRegister();
        });
        
        // 发送验证码
        sendCodeBtn.addEventListener('click', () => {
            this.handleSendCode();
        });
        
        // 邮箱输入验证
        emailInput.addEventListener('input', () => {
            this.clearError('email');
        });
        
        // 验证码输入验证
        codeInput.addEventListener('input', (e) => {
            // 只允许输入数字
            e.target.value = e.target.value.replace(/\D/g, '');
            // 清除错误提示
            this.clearError('code');
        });
        
        // 密码输入验证
        passwordInput.addEventListener('input', () => {
            this.clearError('password');
        });
        
        // 确认密码输入验证
        confirmPasswordInput.addEventListener('input', () => {
            this.clearError('confirmPassword');
        });
        
        // 昵称输入验证
        nicknameInput.addEventListener('input', () => {
            this.clearError('nickname');
        });
    },
    
    /**
     * 验证邮箱
     * @private
     */
    _validateEmail(email) {
        if (!email) {
            return '请输入邮箱';
        }
        
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            return '请输入正确的邮箱地址';
        }
        
        return null;
    },
    
    /**
     * 验证验证码
     * @private
     */
    _validateCode(code) {
        if (!code) {
            return '请输入验证码';
        }
        
        if (!/^\d{6}$/.test(code)) {
            return '验证码为6位数字';
        }
        
        return null;
    },
    
    /**
     * 验证密码
     * @private
     */
    _validatePassword(password) {
        if (!password) {
            return '请输入密码';
        }
        
        if (password.length < 6) {
            return '密码至少6位';
        }
        
        if (password.length > 20) {
            return '密码最多20位';
        }
        
        return null;
    },
    
    /**
     * 验证昵称
     * @private
     */
    _validateNickname(nickname) {
        if (!nickname) {
            return null; // 昵称可选
        }
        
        if (nickname.length < 2) {
            return '昵称至少2个字符';
        }
        
        if (nickname.length > 20) {
            return '昵称最多20个字符';
        }
        
        return null;
    },
    
    /**
     * 显示错误
     */
    showError(field, message) {
        const errorElement = this.elements[`${field}Error`];
        if (errorElement) {
            errorElement.textContent = message;
        }
    },
    
    /**
     * 清除错误
     */
    clearError(field) {
        const errorElement = this.elements[`${field}Error`];
        if (errorElement) {
            errorElement.textContent = '';
        }
    },
    
    /**
     * 显示状态消息
     */
    showStatus(type, message) {
        const { authStatus } = this.elements;
        authStatus.className = `auth-status ${type}`;
        authStatus.textContent = message;
        authStatus.style.display = 'block';
    },
    
    /**
     * 隐藏状态消息
     */
    hideStatus() {
        const { authStatus } = this.elements;
        authStatus.style.display = 'none';
    },
    
    /**
     * 开始倒计时
     * @private
     */
    _startCountdown() {
        const { sendCodeBtn } = this.elements;
        this.countdown = 60;
        sendCodeBtn.disabled = true;
        
        this.countdownTimer = setInterval(() => {
            this.countdown--;
            sendCodeBtn.textContent = `${this.countdown}秒后重试`;
            
            if (this.countdown <= 0) {
                this._stopCountdown();
            }
        }, 1000);
    },
    
    /**
     * 停止倒计时
     * @private
     */
    _stopCountdown() {
        const { sendCodeBtn } = this.elements;
        
        if (this.countdownTimer) {
            clearInterval(this.countdownTimer);
            this.countdownTimer = null;
        }
        
        this.countdown = 0;
        sendCodeBtn.disabled = false;
        sendCodeBtn.textContent = '获取验证码';
    },
    
    /**
     * 处理发送验证码
     */
    async handleSendCode() {
        const { emailInput, sendCodeBtn } = this.elements;
        const email = emailInput.value.trim();
        
        // 验证邮箱
        const emailError = this._validateEmail(email);
        if (emailError) {
            this.showError('email', emailError);
            return;
        }
        
        // 禁用按钮
        sendCodeBtn.disabled = true;
        this.hideStatus();
        
        try {
            this.showStatus('processing', '正在发送验证码...');
            
            // 调用API发送验证码
            await AuthManager.sendEmailCode(email, 'register');
            
            this.showStatus('success', '✅ 验证码已发送，请查收邮箱');
            
            // 开始倒计时
            this._startCountdown();
            
            // 3秒后隐藏成功消息
            setTimeout(() => {
                this.hideStatus();
            }, 3000);
            
        } catch (error) {
            console.error('发送验证码失败:', error);
            this.showStatus('error', `❌ ${error.message}`);
            sendCodeBtn.disabled = false;
        }
    },
    
    /**
     * 处理注册
     */
    async handleRegister() {
        const {
            emailInput, codeInput, passwordInput,
            confirmPasswordInput, nicknameInput, registerBtn
        } = this.elements;
        
        const email = emailInput.value.trim();
        const code = codeInput.value.trim();
        const password = passwordInput.value.trim();
        const confirmPassword = confirmPasswordInput.value.trim();
        const nickname = nicknameInput.value.trim();
        
        // 验证邮箱
        const emailError = this._validateEmail(email);
        if (emailError) {
            this.showError('email', emailError);
            return;
        }
        
        // 验证验证码
        const codeError = this._validateCode(code);
        if (codeError) {
            this.showError('code', codeError);
            return;
        }
        
        // 验证密码
        const passwordError = this._validatePassword(password);
        if (passwordError) {
            this.showError('password', passwordError);
            return;
        }
        
        // 验证确认密码
        if (password !== confirmPassword) {
            this.showError('confirmPassword', '两次密码不一致');
            return;
        }
        
        // 验证昵称
        const nicknameError = this._validateNickname(nickname);
        if (nicknameError) {
            this.showError('nickname', nicknameError);
            return;
        }
        
        // 禁用按钮
        registerBtn.disabled = true;
        this.hideStatus();
        
        try {
            this.showStatus('processing', '正在注册...');
            
            // 调用API注册
            const result = await AuthManager.register({
                email,
                code,
                password,
                nickname: nickname || undefined
            });
            
            this.showStatus('success', `✅ 注册成功！欢迎 ${result.user.nickname || result.user.email}`);
            
            // 1秒后跳转到主页
            setTimeout(() => {
                window.location.href = '/index.html';
            }, 1000);
            
        } catch (error) {
            console.error('注册失败:', error);
            this.showStatus('error', `❌ ${error.message}`);
            registerBtn.disabled = false;
        }
    }
};

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => RegisterPage.init());
} else {
    RegisterPage.init();
}

// 导出供调试使用
window.RegisterPage = RegisterPage;