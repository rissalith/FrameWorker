# 按需启动游戏服务机制

## 概述

为了避免服务器资源消耗过大，游戏库实现了**按需启动游戏服务**的机制。每个用户启动游戏时，系统会为该用户创建独立的游戏服务实例，并在用户不活跃时自动清理。

## 核心特性

### 1. 用户级服务隔离
- 每个用户拥有独立的游戏服务实例
- 不同用户的游戏服务互不干扰
- 支持多用户同时使用同一游戏

### 2. 按需创建
- 只有当用户实际使用游戏功能时才创建服务
- 首次API调用时自动初始化用户的服务实例
- 避免启动时加载所有游戏服务

### 3. 自动清理
- 会话超时自动清理（默认30分钟）
- 后台定期检查并清理过期会话（每5分钟）
- 服务器关闭时自动清理所有会话

### 4. 会话复用
- 用户在超时前重新访问会复用现有会话
- 避免频繁创建和销毁服务实例
- 提高响应速度

## 架构设计

### 会话管理器 (GameSessionManager)

```python
# 位置: GameLibrary/game-session-manager.py

class GameSessionManager:
    """
    游戏会话管理器
    - 管理所有用户的游戏会话
    - 自动清理过期会话
    - 提供会话创建、获取、关闭接口
    """
```

**主要功能**:
- `create_session(user_id, game_id)` - 创建或获取用户会话
- `get_session(session_id)` - 获取指定会话
- `close_session(session_id)` - 关闭会话并清理资源
- 自动清理循环 - 后台线程定期清理过期会话

### 游戏会话 (GameSession)

```python
class GameSession:
    """
    单个游戏会话
    - 存储用户的游戏服务实例
    - 跟踪会话活动时间
    - 提供服务实例的存取接口
    """
```

**会话数据**:
- `user_id` - 用户ID
- `game_id` - 游戏ID
- `services` - 服务实例字典（AI Agent、直播服务等）
- `created_at` - 创建时间
- `last_activity` - 最后活动时间

## 使用方式

### 游戏API集成

游戏后端API需要使用会话管理器来获取用户的服务实例：

```python
# 示例: Fortune-Game API

def get_user_fortune_agent(user_id: str):
    """获取用户的AI Agent实例（按需创建）"""
    session = game_session_manager.create_session(user_id, 'fortune-game')
    
    # 检查会话中是否已有AI Agent
    agent = session.get_service('fortune_agent')
    if agent:
        return agent
    
    # 创建新的AI Agent实例
    agent = FortuneAgentLLMX()
    session.set_service('fortune_agent', agent)
    return agent

@fortune_bp.route('/chat', methods=['POST'])
@verify_token
def fortune_chat():
    """占卜聊天接口"""
    user_id = get_user_id_from_token()
    
    # 按需获取用户的AI Agent
    fortune_agent = get_user_fortune_agent(user_id)
    
    # 使用AI Agent处理请求
    response = fortune_agent.chat(user_input)
    return jsonify({'response': response})
```

### 前端集成

前端无需特殊处理，只需正常调用API：

```javascript
// 前端代码保持不变
const response = await fetch('/api/fortune/chat', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        message: userInput
    })
});
```

## 配置参数

### 会话超时时间

```python
# 在 GameLibrary/game-session-manager.py 中配置
game_session_manager = GameSessionManager(
    session_timeout=30,  # 会话超时时间（分钟）
    cleanup_interval=5   # 清理检查间隔（分钟）
)
```

### 自定义超时时间

不同游戏可以有不同的超时策略：

```python
# 短超时（适合轻量级游戏）
session_timeout=15  # 15分钟

# 长超时（适合需要长时间连接的游戏）
session_timeout=60  # 60分钟
```

## API端点

### 会话管理端点

游戏可以提供以下端点来管理会话：

```
POST /api/{game}/session/close    - 关闭用户会话
GET  /api/{game}/session/status   - 获取会话状态
```

**示例响应**:

```json
{
    "success": true,
    "has_session": true,
    "session_id": "user123_fortune-game_1234567890",
    "created_at": "2024-01-01T00:00:00Z",
    "last_activity": "2024-01-01T00:30:00Z",
    "services": ["fortune_agent", "live_service"],
    "user_id": "user123"
}
```

## 资源清理

### 服务清理接口

游戏服务应该实现清理方法：

```python
class FortuneAgentLLMX:
    def cleanup(self):
        """清理资源"""
        # 关闭连接
        # 释放内存
        # 保存状态
        pass

class LiveService:
    def stop(self):
        """停止服务"""
        # 断开直播连接
        # 清理监听器
        pass
```

### 自动清理流程

1. **会话过期检测**
   - 后台线程每5分钟检查一次
   - 超过30分钟无活动的会话被标记为过期

2. **资源清理**
   - 调用服务的 `cleanup()` 或 `stop()` 方法
   - 从会话管理器中移除会话
   - 释放内存

3. **服务器关闭**
   - 捕获关闭信号
   - 清理所有活跃会话
   - 优雅退出

## 监控和调试

### 日志输出

系统会输出详细的会话管理日志：

```
[GameSessionManager] 创建新会话: user=user123, game=fortune-game, session=user123_fortune-game_1234567890
[Fortune-Game] 为用户 user123 创建AI Agent
[GameSessionManager] 复用会话: user=user123, game=fortune-game, session=user123_fortune-game_1234567890
[GameSessionManager] 清理过期会话: user=user123, game=fortune-game, session=user123_fortune-game_1234567890
[GameSessionManager] 已清理 1 个过期会话
```

### 会话统计

可以通过API获取会话统计信息：

```python
# 获取当前会话数量
session_count = game_session_manager.get_session_count()

# 获取用户的会话数量
user_session_count = game_session_manager.get_user_session_count(user_id)
```

## 性能优化

### 内存使用

- **启动前**: 0个游戏服务实例
- **1个用户**: 1个游戏服务实例
- **10个用户**: 10个游戏服务实例
- **过期清理**: 自动释放不活跃用户的实例

### 响应时间

- **首次请求**: 需要创建服务实例（~100-500ms）
- **后续请求**: 复用现有实例（~10-50ms）
- **会话过期后**: 重新创建实例

### 并发支持

- 使用线程锁保证线程安全
- 支持多用户并发访问
- 每个用户的服务实例独立运行

## 最佳实践

### 1. 合理设置超时时间

```python
# 根据游戏特性设置
- 快速游戏: 15-30分钟
- 直播互动: 30-60分钟
- 长时间游戏: 60-120分钟
```

### 2. 实现清理方法

```python
class GameService:
    def cleanup(self):
        """必须实现清理方法"""
        # 关闭连接
        # 保存状态
        # 释放资源
```

### 3. 更新活动时间

```python
# 在每次API调用时自动更新
session.update_activity()
```

### 4. 错误处理

```python
try:
    agent = get_user_fortune_agent(user_id)
    if not agent:
        # 降级处理
        return default_response()
except Exception as e:
    # 记录错误
    # 返回友好提示
```

## 迁移指南

### 从全局服务迁移

**迁移前**:
```python
# 全局服务实例
fortune_agent = FortuneAgentLLMX()

@app.route('/chat')
def chat():
    response = fortune_agent.chat(message)
    return response
```

**迁移后**:
```python
# 按需创建用户服务
@app.route('/chat')
def chat():
    user_id = get_user_id_from_token()
    fortune_agent = get_user_fortune_agent(user_id)
    response = fortune_agent.chat(message)
    return response
```

### 兼容性

系统支持降级模式，如果会话管理器不可用，会自动使用全局服务：

```python
if SESSION_MANAGER_AVAILABLE:
    # 使用按需启动模式
    agent = get_user_fortune_agent(user_id)
else:
    # 降级到全局服务
    agent = global_fortune_agent
```

## 故障排除

### 问题1: 会话频繁过期

**原因**: 超时时间设置过短

**解决**: 增加 `session_timeout` 参数

### 问题2: 内存持续增长

**原因**: 清理机制未正常工作

**检查**:
- 确认清理线程正在运行
- 检查服务是否实现了清理方法
- 查看日志中的清理记录

### 问题3: 首次请求慢

**原因**: 需要创建服务实例

**优化**:
- 这是正常现象
- 可以实现预热机制
- 或者接受首次延迟

## 总结

按需启动游戏服务机制通过以下方式优化资源使用：

✅ **按需创建** - 只在需要时创建服务
✅ **用户隔离** - 每个用户独立的服务实例
✅ **自动清理** - 过期会话自动释放资源
✅ **会话复用** - 活跃用户复用现有实例
✅ **优雅降级** - 支持回退到全局服务模式

这种设计确保了服务器资源的高效利用，同时保持了良好的用户体验。