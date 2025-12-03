n/**
 * 资源加载工具
 * 提供动态加载JS和CSS的工具函数
 */

/**
 * 动态加载JS文件
 * @param {string} src - JS文件路径
 * @returns {Promise} 加载完成的Promise
 */
window.loadScript = function(src) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
};

/**
 * 动态加载CSS文件
 * @param {string} href - CSS文件路径
 * @returns {Promise} 加载完成的Promise
 */
window.loadStylesheet = function(href) {
    return new Promise((resolve, reject) => {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = href;
        link.onload = resolve;
        link.onerror = reject;
        document.head.appendChild(link);
    });
};