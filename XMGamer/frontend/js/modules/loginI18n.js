/**
 * 登录页国际化(i18n)模块
 * 支持多语言切换
 */

const LoginI18n = {
    // 当前语言 - 默认英文
    currentLang: 'en-US',
    
    // 语言包
    translations: {
        'zh-CN': {
            // 页面标题
            page_title: '登录 - XMGamer',
            
            // 品牌
            brand_subtitle: '我们的关系需要更多想象力',
            
            // 登录表单
            login_title: '登录',
            login_subtitle: '欢迎回来',
            login_btn: '登录',
            
            // 登录模式
            mode_password: '账号密码',
            mode_email: '邮箱验证码',
            
            // 表单字段
            email_placeholder: '邮箱',
            password_placeholder: '密码',
            email_address_placeholder: '邮箱地址',
            code_placeholder: '验证码',
            send_code: '获取验证码',
            resend_code: '秒后重发',
            
            // 第三方登录
            social_login_title: '或使用第三方账号登录',
            google_login: '使用 Google 登录',
            twitter_login: '使用 X 登录',
            
            // 注册
            no_account: '还没有账号？',
            register_now: '立即注册',
            register_title: '创建账号',
            register_subtitle: '加入我们，开始创作',
            register_btn: '注册',
            set_password_placeholder: '设置密码（至少6位）',
            confirm_password_placeholder: '确认密码',
            nickname_placeholder: '昵称（可选）',
            has_account: '已有账号？',
            login_now: '立即登录',
            
            // 设置密码模态框
            set_password_title: '设置登录密码',
            set_password_subtitle: '首次登录，请设置您的密码',
            password_input_placeholder: '请输入密码（至少6位）',
            confirm_input_placeholder: '请再次输入密码',
            skip_btn: '跳过',
            confirm_btn: '确定',
            
            // 首次登录模态框
            first_time_title: '完善账号信息',
            first_time_subtitle: '首次登录，请设置密码和昵称',
            nickname_optional_placeholder: '昵称（选填）',
            
            // 底部链接
            help: '帮助',
            privacy: '隐私权',
            terms: '条款',
            
            // 错误消息
            video_not_supported: '您的浏览器不支持视频播放',
            toggle_volume: '切换音量'
        },
        
        'zh-TW': {
            page_title: '登入 - XMGamer',
            brand_subtitle: '我們的關係需要更多想像力',
            login_title: '登入',
            login_subtitle: '歡迎回來',
            login_btn: '登入',
            mode_password: '帳號密碼',
            mode_email: '郵箱驗證碼',
            email_placeholder: '郵箱',
            password_placeholder: '密碼',
            email_address_placeholder: '郵箱地址',
            code_placeholder: '驗證碼',
            send_code: '獲取驗證碼',
            resend_code: '秒後重發',
            social_login_title: '或使用第三方帳號登入',
            google_login: '使用 Google 登入',
            twitter_login: '使用 X 登入',
            no_account: '還沒有帳號？',
            register_now: '立即註冊',
            register_title: '創建帳號',
            register_subtitle: '加入我們，開始創作',
            register_btn: '註冊',
            set_password_placeholder: '設置密碼（至少6位）',
            confirm_password_placeholder: '確認密碼',
            nickname_placeholder: '暱稱（可選）',
            has_account: '已有帳號？',
            login_now: '立即登入',
            set_password_title: '設置登入密碼',
            set_password_subtitle: '首次登入，請設置您的密碼',
            password_input_placeholder: '請輸入密碼（至少6位）',
            confirm_input_placeholder: '請再次輸入密碼',
            skip_btn: '跳過',
            confirm_btn: '確定',
            first_time_title: '完善帳號資訊',
            first_time_subtitle: '首次登入，請設置密碼和暱稱',
            nickname_optional_placeholder: '暱稱（選填）',
            help: '幫助',
            privacy: '隱私權',
            terms: '條款',
            video_not_supported: '您的瀏覽器不支持視頻播放',
            toggle_volume: '切換音量'
        },
        
        'en-US': {
            page_title: 'Sign in - XMGamer',
            brand_subtitle: 'Our Relationship Needs More Imagination',
            login_title: 'Sign in',
            login_subtitle: 'Welcome back',
            login_btn: 'Sign in',
            mode_password: 'Password',
            mode_email: 'Email Code',
            email_placeholder: 'Email',
            password_placeholder: 'Password',
            email_address_placeholder: 'Email address',
            code_placeholder: 'Verification code',
            send_code: 'Send Code',
            resend_code: 's to resend',
            social_login_title: 'Or sign in with',
            google_login: 'Sign in with Google',
            twitter_login: 'Sign in with X',
            no_account: "Don't have an account?",
            register_now: 'Sign up',
            register_title: 'Create account',
            register_subtitle: 'Join us and start creating',
            register_btn: 'Sign up',
            set_password_placeholder: 'Set password (min 6 chars)',
            confirm_password_placeholder: 'Confirm password',
            nickname_placeholder: 'Nickname (optional)',
            has_account: 'Already have an account?',
            login_now: 'Sign in',
            set_password_title: 'Set Password',
            set_password_subtitle: 'First time login, please set your password',
            password_input_placeholder: 'Enter password (min 6 chars)',
            confirm_input_placeholder: 'Re-enter password',
            skip_btn: 'Skip',
            confirm_btn: 'Confirm',
            first_time_title: 'Complete Profile',
            first_time_subtitle: 'First time login, please set password and nickname',
            nickname_optional_placeholder: 'Nickname (optional)',
            help: 'Help',
            privacy: 'Privacy',
            terms: 'Terms',
            video_not_supported: 'Your browser does not support video playback',
            toggle_volume: 'Toggle volume'
        },
        
        'ja-JP': {
            page_title: 'ログイン - XMGamer',
            brand_subtitle: '私たちの関係にはもっと想像力が必要です',
            login_title: 'ログイン',
            login_subtitle: 'おかえりなさい',
            login_btn: 'ログイン',
            mode_password: 'パスワード',
            mode_email: 'メール認証',
            email_placeholder: 'メール',
            password_placeholder: 'パスワード',
            email_address_placeholder: 'メールアドレス',
            code_placeholder: '認証コード',
            send_code: 'コード送信',
            resend_code: '秒後に再送',
            social_login_title: 'または以下でログイン',
            google_login: 'Googleでログイン',
            twitter_login: 'Xでログイン',
            no_account: 'アカウントをお持ちでないですか？',
            register_now: '新規登録',
            register_title: 'アカウント作成',
            register_subtitle: '参加して創作を始めましょう',
            register_btn: '登録',
            set_password_placeholder: 'パスワード設定（6文字以上）',
            confirm_password_placeholder: 'パスワード確認',
            nickname_placeholder: 'ニックネーム（任意）',
            has_account: 'すでにアカウントをお持ちですか？',
            login_now: 'ログイン',
            set_password_title: 'パスワード設定',
            set_password_subtitle: '初回ログイン、パスワードを設定してください',
            password_input_placeholder: 'パスワードを入力（6文字以上）',
            confirm_input_placeholder: 'パスワードを再入力',
            skip_btn: 'スキップ',
            confirm_btn: '確定',
            first_time_title: 'プロフィール完成',
            first_time_subtitle: '初回ログイン、パスワードとニックネームを設定',
            nickname_optional_placeholder: 'ニックネーム（任意）',
            help: 'ヘルプ',
            privacy: 'プライバシー',
            terms: '利用規約',
            video_not_supported: 'お使いのブラウザは動画再生に対応していません',
            toggle_volume: '音量切替'
        },
        
        'ko-KR': {
            page_title: '로그인 - XMGamer',
            brand_subtitle: '우리의 관계에는 더 많은 상상력이 필요합니다',
            login_title: '로그인',
            login_subtitle: '다시 오신 것을 환영합니다',
            login_btn: '로그인',
            mode_password: '비밀번호',
            mode_email: '이메일 인증',
            email_placeholder: '이메일',
            password_placeholder: '비밀번호',
            email_address_placeholder: '이메일 주소',
            code_placeholder: '인증 코드',
            send_code: '코드 전송',
            resend_code: '초 후 재전송',
            social_login_title: '또는 다음으로 로그인',
            google_login: 'Google로 로그인',
            twitter_login: 'X로 로그인',
            no_account: '계정이 없으신가요?',
            register_now: '가입하기',
            register_title: '계정 만들기',
            register_subtitle: '가입하고 창작을 시작하세요',
            register_btn: '가입',
            set_password_placeholder: '비밀번호 설정 (최소 6자)',
            confirm_password_placeholder: '비밀번호 확인',
            nickname_placeholder: '닉네임 (선택)',
            has_account: '이미 계정이 있으신가요?',
            login_now: '로그인',
            set_password_title: '비밀번호 설정',
            set_password_subtitle: '첫 로그인, 비밀번호를 설정해주세요',
            password_input_placeholder: '비밀번호 입력 (최소 6자)',
            confirm_input_placeholder: '비밀번호 재입력',
            skip_btn: '건너뛰기',
            confirm_btn: '확인',
            first_time_title: '프로필 완성',
            first_time_subtitle: '첫 로그인, 비밀번호와 닉네임을 설정해주세요',
            nickname_optional_placeholder: '닉네임 (선택)',
            help: '도움말',
            privacy: '개인정보',
            terms: '약관',
            video_not_supported: '브라우저가 비디오 재생을 지원하지 않습니다',
            toggle_volume: '음량 전환'
        }
    },
    
    // 语言显示名称
    langNames: {
        'zh-CN': '简体中文',
        'zh-TW': '繁體中文',
        'en-US': 'English',
        'ja-JP': '日本語',
        'ko-KR': '한국어'
    },
    
    /**
     * 初始化
     */
    init() {
        // 优先使用保存的语言，否则默认英文
        const savedLang = localStorage.getItem('preferred_language') || 'en-US';
        this.currentLang = savedLang;
        document.documentElement.lang = savedLang;
        
        // 创建语言切换器
        this._createLanguageSwitcher();
        
        // 应用翻译
        this.applyTranslations();
    },
    
    /**
     * 获取翻译文本
     */
    t(key) {
        const translations = this.translations[this.currentLang] || this.translations['en-US'];
        return translations[key] || key;
    },
    
    /**
     * 切换语言
     */
    setLanguage(lang) {
        if (!this.translations[lang]) {
            console.warn(`[LoginI18n] 不支持的语言: ${lang}`);
            return;
        }
        
        this.currentLang = lang;
        localStorage.setItem('preferred_language', lang);
        document.documentElement.lang = lang;
        this.applyTranslations();
        this._updateSwitcherDisplay();
    },
    
    /**
     * 创建语言切换器
     */
    _createLanguageSwitcher() {
        // 创建语言切换器容器
        const switcher = document.createElement('div');
        switcher.className = 'language-switcher';
        switcher.innerHTML = `
            <button class="lang-btn" id="langSwitcherBtn">
                <svg class="lang-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                </svg>
                <span class="lang-name" id="currentLangName">${this.langNames[this.currentLang]}</span>
                <svg class="arrow-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
            </button>
            <div class="lang-dropdown" id="langDropdown">
                <div class="lang-option" data-lang="en-US">
                    <span class="flag">🇺🇸</span>
                    <span>English</span>
                </div>
                <div class="lang-option" data-lang="zh-CN">
                    <span class="flag">🇨🇳</span>
                    <span>简体中文</span>
                </div>
                <div class="lang-option" data-lang="zh-TW">
                    <span class="flag">🇹🇼</span>
                    <span>繁體中文</span>
                </div>
                <div class="lang-option" data-lang="ja-JP">
                    <span class="flag">🇯🇵</span>
                    <span>日本語</span>
                </div>
                <div class="lang-option" data-lang="ko-KR">
                    <span class="flag">🇰🇷</span>
                    <span>한국어</span>
                </div>
            </div>
        `;
        
        // 添加样式
        const style = document.createElement('style');
        style.textContent = `
            .language-switcher {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
            }
            
            .lang-btn {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 16px;
                background: rgba(255, 255, 255, 0.95);
                border: 1px solid #dadce0;
                border-radius: 24px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                color: #202124;
                transition: all 0.2s ease;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
            
            .lang-btn:hover {
                background: #fff;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
            }
            
            .lang-icon {
                width: 18px;
                height: 18px;
            }
            
            .arrow-icon {
                width: 16px;
                height: 16px;
                transition: transform 0.2s ease;
            }
            
            .language-switcher.open .arrow-icon {
                transform: rotate(180deg);
            }
            
            .lang-dropdown {
                position: absolute;
                top: calc(100% + 8px);
                right: 0;
                min-width: 160px;
                background: #fff;
                border: 1px solid #dadce0;
                border-radius: 12px;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
                overflow: hidden;
                opacity: 0;
                visibility: hidden;
                transform: translateY(-8px);
                transition: all 0.2s ease;
            }
            
            .language-switcher.open .lang-dropdown {
                opacity: 1;
                visibility: visible;
                transform: translateY(0);
            }
            
            .lang-option {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 16px;
                cursor: pointer;
                font-size: 14px;
                color: #202124;
                transition: background 0.15s ease;
            }
            
            .lang-option:hover {
                background: #f1f3f4;
            }
            
            .lang-option.active {
                background: #e8f0fe;
                color: #1a73e8;
            }
            
            .lang-option .flag {
                font-size: 18px;
            }
            
            @media (max-width: 768px) {
                .language-switcher {
                    top: 10px;
                    right: 10px;
                }
                
                .lang-btn {
                    padding: 6px 12px;
                    font-size: 13px;
                }
                
                .lang-name {
                    display: none;
                }
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(switcher);
        
        // 绑定事件
        const btn = document.getElementById('langSwitcherBtn');
        const dropdown = document.getElementById('langDropdown');
        
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            switcher.classList.toggle('open');
        });
        
        document.addEventListener('click', () => {
            switcher.classList.remove('open');
        });
        
        dropdown.querySelectorAll('.lang-option').forEach(option => {
            option.addEventListener('click', (e) => {
                e.stopPropagation();
                const lang = option.dataset.lang;
                this.setLanguage(lang);
                switcher.classList.remove('open');
            });
        });
        
        // 更新当前选中状态
        this._updateSwitcherDisplay();
    },
    
    /**
     * 更新切换器显示
     */
    _updateSwitcherDisplay() {
        const langName = document.getElementById('currentLangName');
        if (langName) {
            langName.textContent = this.langNames[this.currentLang];
        }
        
        document.querySelectorAll('.lang-option').forEach(option => {
            if (option.dataset.lang === this.currentLang) {
                option.classList.add('active');
            } else {
                option.classList.remove('active');
            }
        });
    },
    
    /**
     * 应用翻译到页面
     */
    applyTranslations() {
        // 页面标题
        document.title = this.t('page_title');
        
        // 品牌副标题
        const brandSubtitle = document.querySelector('.brand-subtitle');
        if (brandSubtitle) brandSubtitle.textContent = this.t('brand_subtitle');
        
        // 登录标题
        const authTitle = document.querySelector('#loginHeader .auth-title');
        if (authTitle) authTitle.textContent = this.t('login_title');
        
        const authSubtitle = document.querySelector('#loginHeader .auth-subtitle');
        if (authSubtitle) authSubtitle.textContent = this.t('login_subtitle');
        
        // 登录模式按钮
        const modeBtns = document.querySelectorAll('.mode-btn');
        modeBtns.forEach(btn => {
            if (btn.dataset.mode === 'password') {
                btn.textContent = this.t('mode_password');
            } else if (btn.dataset.mode === 'email') {
                btn.textContent = this.t('mode_email');
            }
        });
        
        // 表单字段
        const accountInput = document.getElementById('accountInput');
        if (accountInput) accountInput.placeholder = this.t('email_placeholder');
        
        const passwordInput = document.getElementById('passwordInput');
        if (passwordInput) passwordInput.placeholder = this.t('password_placeholder');
        
        const emailInput = document.getElementById('emailInput');
        if (emailInput) emailInput.placeholder = this.t('email_address_placeholder');
        
        const codeInput = document.getElementById('codeInput');
        if (codeInput) codeInput.placeholder = this.t('code_placeholder');
        
        const sendCodeBtn = document.getElementById('sendCodeBtn');
        if (sendCodeBtn && !sendCodeBtn.disabled) {
            sendCodeBtn.textContent = this.t('send_code');
        }
        
        // 第三方登录
        const socialTitle = document.querySelector('.social-login-title');
        if (socialTitle) socialTitle.textContent = this.t('social_login_title');
        
        const googleBtn = document.getElementById('googleLoginBtn');
        if (googleBtn) googleBtn.title = this.t('google_login');
        
        const twitterBtn = document.getElementById('twitterLoginBtn');
        if (twitterBtn) twitterBtn.title = this.t('twitter_login');
        
        // 登录按钮
        const loginBtn = document.getElementById('loginBtn');
        if (loginBtn) loginBtn.textContent = this.t('login_btn');
        
        // 登录页脚
        const loginFooterText = document.querySelector('#loginFooter .footer-text');
        if (loginFooterText) loginFooterText.textContent = this.t('no_account');
        
        const showRegisterBtn = document.getElementById('showRegisterBtn');
        if (showRegisterBtn) showRegisterBtn.textContent = this.t('register_now');
        
        // 注册表单
        const registerEmailInput = document.getElementById('registerEmailInput');
        if (registerEmailInput) registerEmailInput.placeholder = this.t('email_address_placeholder');
        
        const registerCodeInput = document.getElementById('registerCodeInput');
        if (registerCodeInput) registerCodeInput.placeholder = this.t('code_placeholder');
        
        const registerSendCodeBtn = document.getElementById('registerSendCodeBtn');
        if (registerSendCodeBtn && !registerSendCodeBtn.disabled) {
            registerSendCodeBtn.textContent = this.t('send_code');
        }
        
        const registerPasswordInput = document.getElementById('registerPasswordInput');
        if (registerPasswordInput) registerPasswordInput.placeholder = this.t('set_password_placeholder');
        
        const registerConfirmPasswordInput = document.getElementById('registerConfirmPasswordInput');
        if (registerConfirmPasswordInput) registerConfirmPasswordInput.placeholder = this.t('confirm_password_placeholder');
        
        const registerNicknameInput = document.getElementById('registerNicknameInput');
        if (registerNicknameInput) registerNicknameInput.placeholder = this.t('nickname_placeholder');
        
        const registerBtn = document.getElementById('registerBtn');
        if (registerBtn) registerBtn.textContent = this.t('register_btn');
        
        const registerFooterText = document.querySelector('#registerFooter .footer-text');
        if (registerFooterText) registerFooterText.textContent = this.t('has_account');
        
        const showLoginBtn = document.getElementById('showLoginBtn');
        if (showLoginBtn) showLoginBtn.textContent = this.t('login_now');
        
        // 设置密码模态框
        const setPasswordTitle = document.querySelector('#setPasswordModal .modal-header h3');
        if (setPasswordTitle) setPasswordTitle.textContent = this.t('set_password_title');
        
        const setPasswordSubtitle = document.querySelector('#setPasswordModal .modal-subtitle');
        if (setPasswordSubtitle) setPasswordSubtitle.textContent = this.t('set_password_subtitle');
        
        const newPassword = document.getElementById('newPassword');
        if (newPassword) newPassword.placeholder = this.t('password_input_placeholder');
        
        const confirmPassword = document.getElementById('confirmPassword');
        if (confirmPassword) confirmPassword.placeholder = this.t('confirm_input_placeholder');
        
        const skipBtn = document.getElementById('skipPasswordBtn');
        if (skipBtn) skipBtn.textContent = this.t('skip_btn');
        
        const confirmPasswordBtn = document.getElementById('confirmPasswordBtn');
        if (confirmPasswordBtn) confirmPasswordBtn.textContent = this.t('confirm_btn');
        
        // 首次登录模态框
        const firstTimeTitle = document.querySelector('#firstTimeLoginModal .modal-header h3');
        if (firstTimeTitle) firstTimeTitle.textContent = this.t('first_time_title');
        
        const firstTimeSubtitle = document.querySelector('#firstTimeLoginModal .modal-subtitle');
        if (firstTimeSubtitle) firstTimeSubtitle.textContent = this.t('first_time_subtitle');
        
        const firstTimePassword = document.getElementById('firstTimePassword');
        if (firstTimePassword) firstTimePassword.placeholder = this.t('set_password_placeholder');
        
        const firstTimeConfirmPassword = document.getElementById('firstTimeConfirmPassword');
        if (firstTimeConfirmPassword) firstTimeConfirmPassword.placeholder = this.t('confirm_password_placeholder');
        
        const firstTimeNickname = document.getElementById('firstTimeNickname');
        if (firstTimeNickname) firstTimeNickname.placeholder = this.t('nickname_optional_placeholder');
        
        const confirmFirstTimeBtn = document.getElementById('confirmFirstTimeBtn');
        if (confirmFirstTimeBtn) confirmFirstTimeBtn.textContent = this.t('confirm_btn');
        
        // 底部链接
        const bottomLinks = document.querySelectorAll('.bottom-links .link');
        if (bottomLinks.length >= 4) {
            bottomLinks[0].textContent = this.langNames[this.currentLang];
            bottomLinks[1].textContent = this.t('help');
            bottomLinks[2].textContent = this.t('privacy');
            bottomLinks[3].textContent = this.t('terms');
        }
        
        // 音量按钮
        const volumeToggle = document.getElementById('volumeToggle');
        if (volumeToggle) volumeToggle.setAttribute('aria-label', this.t('toggle_volume'));
    }
};

// 页面加载时初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => LoginI18n.init());
} else {
    LoginI18n.init();
}

// 导出
window.LoginI18n = LoginI18n;

