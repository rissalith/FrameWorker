/**
 * 钱包管理页面
 */

const API_BASE = 'http://localhost:3000/api';

// 状态管理
const state = {
    wallet: null,
    transactions: [],
    rechargePackages: [],
    currentFilter: 'all',
    currentPage: 1,
    pageSize: 20,
    totalTransactions: 0,
    selectedPackage: null
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    initEventListeners();
    loadWalletInfo();
    loadRechargePackages();
    loadTransactions();
});

// 检查认证
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = '../login.html';
        return;
    }

    // 加载用户信息
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    document.getElementById('userNickname').textContent = user.nickname || '用户';
}

// 初始化事件监听
function initEventListeners() {
    // 退出登录
    document.getElementById('logoutBtn').addEventListener('click', () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '../login.html';
    });

    // 充值按钮
    document.getElementById('rechargeBtn').addEventListener('click', () => {
        showRechargeModal();
    });

    // 筛选标签
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            state.currentFilter = e.target.dataset.type;
            state.currentPage = 1;
            loadTransactions();
        });
    });

    // 分页
    document.getElementById('prevPage').addEventListener('click', () => {
        if (state.currentPage > 1) {
            state.currentPage--;
            loadTransactions();
        }
    });

    document.getElementById('nextPage').addEventListener('click', () => {
        const totalPages = Math.ceil(state.totalTransactions / state.pageSize);
        if (state.currentPage < totalPages) {
            state.currentPage++;
            loadTransactions();
        }
    });

    // 模态框关闭
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.target.closest('.modal').style.display = 'none';
        });
    });

    // 点击模态框外部关闭
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });
}

// 加载钱包信息
async function loadWalletInfo() {
    try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE}/wallet`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        if (data.success) {
            state.wallet = data.wallet;
            updateWalletUI();
        } else {
            showError('加载钱包信息失败');
        }
    } catch (error) {
        console.error('加载钱包信息错误:', error);
        showError('网络错误');
    }
}

// 更新钱包UI
function updateWalletUI() {
    if (!state.wallet) return;

    document.getElementById('currentBalance').textContent = state.wallet.balance.toLocaleString();
    document.getElementById('totalRecharged').textContent = state.wallet.total_recharged.toLocaleString();
    document.getElementById('totalConsumed').textContent = state.wallet.total_consumed.toLocaleString();
    document.getElementById('frozenBalance').textContent = state.wallet.frozen_balance.toLocaleString();
}

// 加载充值套餐
async function loadRechargePackages() {
    try {
        const response = await fetch(`${API_BASE}/products?category=recharge`);
        const data = await response.json();
        
        if (data.success) {
            state.rechargePackages = data.products;
        }
    } catch (error) {
        console.error('加载充值套餐错误:', error);
    }
}

// 显示充值弹窗
function showRechargeModal() {
    const modal = document.getElementById('rechargeModal');
    const container = document.getElementById('rechargePackages');

    if (state.rechargePackages.length === 0) {
        container.innerHTML = '<div class="empty-state">暂无充值套餐</div>';
    } else {
        container.innerHTML = state.rechargePackages.map(pkg => {
            const bonus = pkg.price > 100 ? Math.round((pkg.price - 100) / 100 * 10) : 0;
            return `
                <div class="package-card" onclick="selectPackage('${pkg.id}')">
                    ${bonus > 0 ? `<div class="package-badge">+${bonus}%</div>` : ''}
                    <div class="package-amount">
                        ${pkg.price}
                        <span class="package-unit">点</span>
                    </div>
                    <div class="package-price">¥${pkg.price_cny}</div>
                    <div class="package-desc">${pkg.description || ''}</div>
                </div>
            `;
        }).join('');
    }

    modal.style.display = 'flex';
}

// 选择充值套餐
window.selectPackage = function(packageId) {
    const pkg = state.rechargePackages.find(p => p.id === packageId);
    if (!pkg) return;

    state.selectedPackage = pkg;
    document.getElementById('rechargeModal').style.display = 'none';
    showPaymentModal(pkg);
};

// 显示支付弹窗
function showPaymentModal(pkg) {
    const modal = document.getElementById('paymentModal');
    document.getElementById('payAmount').textContent = pkg.price.toLocaleString();
    document.getElementById('payCny').textContent = `¥${pkg.price_cny}`;

    // 绑定支付方式点击事件
    document.querySelectorAll('.payment-btn').forEach(btn => {
        btn.onclick = () => processPayment(pkg.id, btn.dataset.method);
    });

    modal.style.display = 'flex';
}

// 处理支付
async function processPayment(productId, paymentMethod) {
    try {
        const token = localStorage.getItem('token');
        
        // 1. 创建充值订单
        const orderResponse = await fetch(`${API_BASE}/wallet/recharge`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                product_id: productId,
                payment_method: paymentMethod
            })
        });

        const orderData = await orderResponse.json();
        if (!orderData.success) {
            showError(orderData.message || '创建订单失败');
            return;
        }

        // 2. 模拟支付成功（测试环境）
        showInfo('正在处理支付...');
        await new Promise(resolve => setTimeout(resolve, 1500));

        // 3. 完成充值
        const completeResponse = await fetch(`${API_BASE}/wallet/recharge/complete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                order_id: orderData.order_id,
                payment_id: `test_${Date.now()}`
            })
        });

        const completeData = await completeResponse.json();
        if (completeData.success) {
            document.getElementById('paymentModal').style.display = 'none';
            showSuccess(`充值成功！获得 ${completeData.amount} 点`);
            
            // 刷新数据
            await loadWalletInfo();
            await loadTransactions();
        } else {
            showError(completeData.message || '充值失败');
        }

    } catch (error) {
        console.error('支付处理错误:', error);
        showError('支付处理失败');
    }
}

// 加载交易记录
async function loadTransactions() {
    try {
        const token = localStorage.getItem('token');
        const type = state.currentFilter === 'all' ? '' : state.currentFilter;
        const offset = (state.currentPage - 1) * state.pageSize;

        const url = `${API_BASE}/wallet/transactions?type=${type}&limit=${state.pageSize}&offset=${offset}`;
        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        const data = await response.json();
        if (data.success) {
            state.transactions = data.transactions;
            state.totalTransactions = data.total;
            updateTransactionsUI();
            updatePaginationUI();
        }
    } catch (error) {
        console.error('加载交易记录错误:', error);
        showError('加载交易记录失败');
    }
}

// 更新交易记录UI
function updateTransactionsUI() {
    const container = document.getElementById('transactionList');

    if (state.transactions.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📝</div>
                <p>暂无交易记录</p>
            </div>
        `;
        return;
    }

    container.innerHTML = state.transactions.map(tx => {
        const isPositive = tx.amount > 0;
        const typeMap = {
            'DEPOSIT': { icon: '💰', text: '充值', class: 'deposit' },
            'PURCHASE': { icon: '🎮', text: '购买', class: 'purchase' },
            'REFUND': { icon: '↩️', text: '退款', class: 'refund' },
            'REWARD': { icon: '🎁', text: '奖励', class: 'deposit' }
        };
        const typeInfo = typeMap[tx.type] || { icon: '📝', text: tx.type, class: 'purchase' };

        return `
            <div class="transaction-item">
                <div class="transaction-icon ${typeInfo.class}">
                    ${typeInfo.icon}
                </div>
                <div class="transaction-info">
                    <div class="transaction-title">${tx.product_name || typeInfo.text}</div>
                    <div class="transaction-desc">${tx.description || ''}</div>
                    <div class="transaction-desc">订单号: ${tx.order_id || '-'}</div>
                </div>
                <div class="transaction-amount">
                    <div class="amount-value ${isPositive ? 'positive' : 'negative'}">
                        ${isPositive ? '+' : ''}${tx.amount.toLocaleString()}
                    </div>
                    <div class="transaction-time">${formatDate(tx.created_at)}</div>
                    <span class="transaction-status ${tx.status}">${getStatusText(tx.status)}</span>
                </div>
            </div>
        `;
    }).join('');
}

// 更新分页UI
function updatePaginationUI() {
    const totalPages = Math.ceil(state.totalTransactions / state.pageSize);
    document.getElementById('pageInfo').textContent = `第 ${state.currentPage} / ${totalPages} 页`;
    document.getElementById('prevPage').disabled = state.currentPage === 1;
    document.getElementById('nextPage').disabled = state.currentPage >= totalPages;
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return '刚刚';
    if (minutes < 60) return `${minutes}分钟前`;
    if (hours < 24) return `${hours}小时前`;
    if (days < 7) return `${days}天前`;

    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 获取状态文本
function getStatusText(status) {
    const statusMap = {
        'completed': '已完成',
        'pending': '处理中',
        'failed': '失败'
    };
    return statusMap[status] || status;
}

// 提示消息
function showSuccess(message) {
    alert('✅ ' + message);
}

function showError(message) {
    alert('❌ ' + message);
}

function showInfo(message) {
    alert('ℹ️ ' + message);
}