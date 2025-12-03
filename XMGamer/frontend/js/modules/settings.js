/**
 * 个人设置模块
 * 处理用户设置相关的所有功能
 */

const SettingsManager = {
    /**
     * 初始化设置管理器
     */
    init() {
        console.log('[设置] 初始化设置管理器...');
        
        // 加载用户信息
        this._loadUserInfo();
        
        // 绑定标签切换事件
        this._bindTabEvents();
        
        // 绑定表单事件
        this._bindFormEvents();
        
        // 加载用户偏好设置
        this._loadPreferences();
        
        console.log('[设置] 设置管理器已初始化 ✅');
    },
    
    /**
     * 加载用户信息
     * @private
     */
    async _loadUserInfo() {
        try {
            const user = AuthManager.getCurrentUser();
            if (!user) {
                const userData = await AuthManager.getUserInfo();
                this._updateUserDisplay(userData);
            } else {
                this._updateUserDisplay(user);
            }
        } catch (error) {
            console.error('[设置] 加载用户信息失败:', error);
            this._showMessage('error', '加载用户信息失败');
        }
    },
    
    /**
     * 更新用户信息显示
     * @private
     */
    _updateUserDisplay(user) {
        // 更新昵称
        const nicknameInput = document.getElementById('nicknameInput');
        if (nicknameInput && user.nickname) {
            nicknameInput.value = user.nickname;
        }
        
        // 更新邮箱
        const emailDisplay = document.getElementById('emailDisplay');
        if (emailDisplay && user.email) {
            emailDisplay.value = user.email;
        }
        
        // 更新头像
        const avatarPreview = document.getElementById('avatarPreview');
        if (avatarPreview && user.avatar_url) {
            avatarPreview.innerHTML = `<img src="${user.avatar_url}" alt="头像">`;
        }
    },
    
    /**
     * 绑定标签切换事件
     * @private
     */
    _bindTabEvents() {
        const navItems = document.querySelectorAll('.settings-nav-item');
        const panels = document.querySelectorAll('.settings-panel');
        
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                const tabName = item.dataset.tab;
                
                // 更新导航状态
                navItems.forEach(nav => nav.classList.remove('active'));
                item.classList.add('active');
                
                // 更新面板显示
                panels.forEach(panel => panel.classList.remove('active'));
                const targetPanel = document.getElementById(`${tabName}-panel`);
                if (targetPanel) {
                    targetPanel.classList.add('active');
                }
            });
        });
    },
    
    /**
     * 绑定表单事件
     * @private
     */
    _bindFormEvents() {
        // 头像上传
        this._bindAvatarUpload();
        
        // 保存个人资料
        this._bindSaveProfile();
        
        // 修改密码
        this._bindChangePassword();
        
        // 密码显示/隐藏
        this._bindPasswordToggle();
        
        // 保存语言设置
        this._bindSaveLanguage();
        
        // 偏好设置开关
        this._bindPreferenceToggles();
    },
    
    /**
     * 绑定头像上传
     * @private
     */
    _bindAvatarUpload() {
        const uploadBtn = document.getElementById('uploadAvatarBtn');
        const avatarInput = document.getElementById('avatarInput');
        const avatarPreview = document.getElementById('avatarPreview');
        
        if (uploadBtn && avatarInput) {
            uploadBtn.addEventListener('click', () => {
                avatarInput.click();
            });
            
            avatarInput.addEventListener('change', async (e) => {
                const file = e.target.files[0];
                if (!file) return;
                
                // 验证文件类型
                if (!file.type.startsWith('image/')) {
                    this._showMessage('error', '请选择图片文件');
                    return;
                }
                
                // 验证文件大小（最大2MB）
                if (file.size > 2 * 1024 * 1024) {
                    this._showMessage('error', '图片大小不能超过2MB');
                    return;
                }
                
                // 预览图片
                const reader = new FileReader();
                reader.onload = (e) => {
                    avatarPreview.innerHTML = `<img src="${e.target.result}" alt="头像">`;
                };
                reader.readAsDataURL(file);
                
                // TODO: 上传到服务器
                // await this._uploadAvatar(file);
            });
        }
    },
    
    /**
     * 绑定保存个人资料
     * @private
     */
    _bindSaveProfile() {
        const saveBtn = document.getElementById('saveProfileBtn');
        const nicknameInput = document.getElementById('nicknameInput');
        
        if (saveBtn && nicknameInput) {
            saveBtn.addEventListener('click', async () => {
                const nickname = nicknameInput.value.trim();
                
                // 验证昵称
                if (!nickname) {
                    this._showMessage('error', '请输入昵称', 'profile-panel');
                    return;
                }
                
                if (nickname.length < 2 || nickname.length > 20) {
                    this._showMessage('error', '昵称长度为2-20个字符', 'profile-panel');
                    return;
                }
                
                try {
                    saveBtn.disabled = true;
                    saveBtn.textContent = '保存中...';
                    
                    // 调用API更新用户信息
                    await AuthManager.updateProfile({ nickname });
                    
                    this._showMessage('success', '个人资料已更新', 'profile-panel');
                    
                    // 更新主页面的用户名显示
                    const userNameEl = document.querySelector('.user-name');
                    if (userNameEl) {
                        userNameEl.textContent = nickname;
                    }
                } catch (error) {
                    console.error('[设置] 保存个人资料失败:', error);
                    this._showMessage('error', error.message || '保存失败，请重试', 'profile-panel');
                } finally {
                    saveBtn.disabled = false;
                    saveBtn.innerHTML = `
                        <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                        保存修改
                    `;
                }
            });
        }
    },
    
    /**
     * 绑定修改密码
     * @private
     */
    _bindChangePassword() {
        const changeBtn = document.getElementById('changePasswordBtn');
        const currentPassword = document.getElementById('currentPassword');
        const newPassword = document.getElementById('newPassword');
        const confirmPassword = document.getElementById('confirmPassword');
        
        if (changeBtn && currentPassword && newPassword && confirmPassword) {
            changeBtn.addEventListener('click', async () => {
                const current = currentPassword.value.trim();
                const newPwd = newPassword.value.trim();
                const confirm = confirmPassword.value.trim();
                
                // 验证输入
                if (!current) {
                    this._showMessage('error', '请输入当前密码', 'security-panel');
                    return;
                }
                
                if (!newPwd) {
                    this._showMessage('error', '请输入新密码', 'security-panel');
                    return;
                }
                
                if (newPwd.length < 6 || newPwd.length > 20) {
                    this._showMessage('error', '密码长度为6-20个字符', 'security-panel');
                    return;
                }
                
                if (newPwd !== confirm) {
                    this._showMessage('error', '两次输入的密码不一致', 'security-panel');
                    return;
                }
                
                if (current === newPwd) {
                    this._showMessage('error', '新密码不能与当前密码相同', 'security-panel');
                    return;
                }
                
                try {
                    changeBtn.disabled = true;
                    changeBtn.textContent = '修改中...';
                    
                    // 调用API修改密码
                    await this._changePassword(current, newPwd);
                    
                    this._showMessage('success', '密码修改成功', 'security-panel');
                    
                    // 清空输入框
                    currentPassword.value = '';
                    newPassword.value = '';
                    confirmPassword.value = '';
                } catch (error) {
                    console.error('[设置] 修改密码失败:', error);
                    this._showMessage('error', error.message || '修改失败，请重试', 'security-panel');
                } finally {
                    changeBtn.disabled = false;
                    changeBtn.innerHTML = `
                        <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                        修改密码
                    `;
                }
            });
        }
    },
    
    /**
     * 修改密码API调用
     * @private
     */
    async _changePassword(currentPassword, newPassword) {
        const response = await AuthManager.authenticatedFetch(
            `${AuthManager.apiBaseUrl}/auth/change-password`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword
                })
            }
        );
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || data.error || '修改密码失败');
        }
        
        return data;
    },
    
    /**
     * 绑定密码显示/隐藏
     * @private
     */
    _bindPasswordToggle() {
        const toggleButtons = document.querySelectorAll('.password-toggle');
        
        toggleButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetId = button.dataset.target;
                const input = document.getElementById(targetId);
                
                if (input) {
                    const isPassword = input.type === 'password';
                    input.type = isPassword ? 'text' : 'password';
                    
                    // 更新图标
                    const icon = button.querySelector('.eye-icon');
                    if (icon) {
                        if (isPassword) {
                            // 显示"眼睛关闭"图标
                            icon.innerHTML = `
                                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                                <line x1="1" y1="1" x2="23" y2="23"></line>
                            `;
                        } else {
                            // 显示"眼睛睁开"图标
                            icon.innerHTML = `
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                                <circle cx="12" cy="12" r="3"></circle>
                            `;
                        }
                    }
                }
            });
        });
    },
    
    /**
     * 绑定保存语言设置
     * @private
     */
    _bindSaveLanguage() {
        const saveBtn = document.getElementById('saveLanguageBtn');
        const languageRadios = document.querySelectorAll('input[name="language"]');
        
        if (saveBtn && languageRadios.length > 0) {
            saveBtn.addEventListener('click', () => {
                const selectedLanguage = document.querySelector('input[name="language"]:checked');
                
                if (selectedLanguage) {
                    const language = selectedLanguage.value;
                    
                    // 保存到localStorage
                    localStorage.setItem('preferred_language', language);
                    
                    this._showMessage('success', '语言设置已保存', 'language-panel');
                    
                    // TODO: 实际应用语言切换
                    console.log('[设置] 语言已切换为:', language);
                }
            });
        }
    },
    
    /**
     * 绑定偏好设置开关
     * @private
     */
    _bindPreferenceToggles() {
        const darkModeToggle = document.getElementById('darkModeToggle');
        const animationToggle = document.getElementById('animationToggle');
        const desktopNotificationToggle = document.getElementById('desktopNotificationToggle');
        const soundToggle = document.getElementById('soundToggle');
        
        // 深色模式
        if (darkModeToggle) {
            darkModeToggle.addEventListener('change', (e) => {
                const enabled = e.target.checked;
                localStorage.setItem('dark_mode', enabled);
                this._applyDarkMode(enabled);
            });
        }
        
        // 动画效果
        if (animationToggle) {
            animationToggle.addEventListener('change', (e) => {
                const enabled = e.target.checked;
                localStorage.setItem('animations_enabled', enabled);
                document.body.classList.toggle('no-animations', !enabled);
            });
        }
        
        // 桌面通知
        if (desktopNotificationToggle) {
            desktopNotificationToggle.addEventListener('change', async (e) => {
                const enabled = e.target.checked;
                
                if (enabled && 'Notification' in window) {
                    const permission = await Notification.requestPermission();
                    if (permission !== 'granted') {
                        e.target.checked = false;
                        this._showMessage('error', '通知权限被拒绝', 'preferences-panel');
                        return;
                    }
                }
                
                localStorage.setItem('desktop_notifications', enabled);
            });
        }
        
        // 声音提示
        if (soundToggle) {
            soundToggle.addEventListener('change', (e) => {
                const enabled = e.target.checked;
                localStorage.setItem('sound_enabled', enabled);
            });
        }
    },
    
    /**
     * 加载用户偏好设置
     * @private
     */
    _loadPreferences() {
        // 加载深色模式
        const darkMode = localStorage.getItem('dark_mode') === 'true';
        const darkModeToggle = document.getElementById('darkModeToggle');
        if (darkModeToggle) {
            darkModeToggle.checked = darkMode;
            this._applyDarkMode(darkMode);
        }
        
        // 加载动画设置
        const animationsEnabled = localStorage.getItem('animations_enabled') !== 'false';
        const animationToggle = document.getElementById('animationToggle');
        if (animationToggle) {
            animationToggle.checked = animationsEnabled;
            document.body.classList.toggle('no-animations', !animationsEnabled);
        }
        
        // 加载通知设置
        const desktopNotifications = localStorage.getItem('desktop_notifications') === 'true';
        const desktopNotificationToggle = document.getElementById('desktopNotificationToggle');
        if (desktopNotificationToggle) {
            desktopNotificationToggle.checked = desktopNotifications;
        }
        
        // 加载声音设置
        const soundEnabled = localStorage.getItem('sound_enabled') !== 'false';
        const soundToggle = document.getElementById('soundToggle');
        if (soundToggle) {
            soundToggle.checked = soundEnabled;
        }
        
        // 加载语言设置
        const preferredLanguage = localStorage.getItem('preferred_language') || 'zh-CN';
        const languageRadio = document.querySelector(`input[name="language"][value="${preferredLanguage}"]`);
        if (languageRadio) {
            languageRadio.checked = true;
        }
    },
    
    /**
     * 应用深色模式
     * @private
     */
    _applyDarkMode(enabled) {
        if (enabled) {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    },
    
    /**
     * 显示消息提示
     * @private
     */
    _showMessage(type, message, panelId = null) {
        const panel = panelId ? document.getElementById(panelId) : document.querySelector('.settings-panel.active');
        if (!panel) return;
        
        // 移除旧消息
        const oldMessage = panel.querySelector('.form-message');
        if (oldMessage) {
            oldMessage.remove();
        }
        
        // 创建新消息
        const messageEl = document.createElement('div');
        messageEl.className = `form-message ${type}`;
        
        const icon = type === 'success' 
            ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>'
            : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>';
        
        messageEl.innerHTML = `${icon}<span>${message}</span>`;
        
        // 插入到面板顶部
        const firstSection = panel.querySelector('.panel-section');
        if (firstSection) {
            firstSection.insertBefore(messageEl, firstSection.firstChild);
        }
        
        // 3秒后自动移除
        setTimeout(() => {
            messageEl.remove();
        }, 3000);
    }
};

// 导出模块
window.SettingsManager = SettingsManager;