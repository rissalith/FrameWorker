/**
 * OAuth 第三方登录配置
 * 
 * 使用说明：
 * 1. 在各平台创建 OAuth 应用
 * 2. 将获取的 Client ID 填入下方配置
 * 3. 在后端设置对应的环境变量
 */

// OAuth 配置
window.OAUTH_CONFIG = {
    // Google OAuth 2.0
    // 申请地址: https://console.cloud.google.com/apis/credentials
    GOOGLE_CLIENT_ID: '905113829240-it9vejm24bgnqfqqm167g8qeu1661jl9.apps.googleusercontent.com',
    
    // Twitter/X OAuth 2.0
    // 申请地址: https://developer.twitter.com/en/portal/dashboard
    TWITTER_CLIENT_ID: 'Y05TdWhBWXJhdUxVdlRLQnVLcEc6MTpjaQ'
};

// 将配置挂载到全局
window.GOOGLE_CLIENT_ID = window.OAUTH_CONFIG.GOOGLE_CLIENT_ID;
window.TWITTER_CLIENT_ID = window.OAUTH_CONFIG.TWITTER_CLIENT_ID;

console.log('OAuth配置已加载');