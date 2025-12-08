# Fortune-Game 后端说明

## Pylance警告说明

您看到的Pylance警告是正常的，这是由于以下原因：

### 1. 动态导入和条件导入

```python
try:
    from services.fortune_agent_llmx import FortuneAgentLLMX
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
```

Pylance无法在静态分析时确定这些导入是否成功，所以会报告"possibly unbound"警告。但在运行时，代码会正确处理这些情况。

### 2. 智能降级机制

代码实现了智能降级：
- 如果AI服务不可用 → 使用默认回复
- 如果直播服务不可用 → 模拟模式运行
- 所有功能都有fallback机制

### 3. 这些警告不影响运行

✅ 代码在运行时会正确工作
✅ 所有异常都有妥善处理
✅ 服务不可用时会优雅降级

## 如何消除警告（可选）

如果您想消除这些警告，可以：

### 方法1: 添加类型注解

```python
from typing import Optional

fortune_agent: Optional[FortuneAgentLLMX] = None
live_service: Optional[LiveService] = None
```

### 方法2: 使用类型忽略注释

```python
from services.fortune_agent_llmx import FortuneAgentLLMX  # type: ignore
```

### 方法3: 配置Pylance

在`.vscode/settings.json`中：

```json
{
    "python.analysis.diagnosticSeverityOverrides": {
        "reportPossiblyUnboundVariable": "none",
        "reportAttributeAccessIssue": "none"
    }
}
```

## 后端功能说明

### AI Agent功能

**文件**: `services/fortune_agent_llmx.py`

**功能**:
- 使用LLMX API进行智能对话
- 基于知识库的角色扮演
- 上下文理解和记忆

**配置**:
需要在环境变量中设置LLMX API密钥

### 直播功能

**文件**: `services/douyin/live_monitor.py`

**功能**:
- 抖音直播间实时监听
- 弹幕接收和处理
- 礼物映射到占卜类型

**配置**:
需要配置直播间ID

### 知识库

**目录**: `knowledge_base/`

**内容**:
- 角色设定
- 占卜规则
- 语言风格
- 互动场景
- 限制条件
- 游戏机制
- 示例对话

## API端点

所有端点都需要JWT令牌认证（通过Authorization header）

### 1. 占卜聊天
```
POST /api/fortune/chat
Content-Type: application/json
Authorization: Bearer <token>

{
  "message": "用户消息",
  "username": "用户名",
  "grade": "签级",
  "topic": "占卜类型"
}
```

### 2. 启动直播监听
```
POST /api/fortune/live/start
Content-Type: application/json
Authorization: Bearer <token>

{
  "live_id": "直播间ID"
}
```

### 3. 停止直播监听
```
POST /api/fortune/live/stop
Content-Type: application/json
Authorization: Bearer <token>

{
  "live_id": "直播间ID"
}
```

### 4. 获取直播状态
```
GET /api/fortune/live/status
Authorization: Bearer <token>
```

### 5. 随机占卜
```
GET /api/fortune/fortune/random?type=daily
Authorization: Bearer <token>
```

### 6. 礼物映射
```
GET /api/fortune/gift/mapping
```

### 7. 游戏配置
```
GET /api/fortune/config
```

## 依赖说明

### Python依赖

查看 `games/backend/requirements.txt` 了解完整依赖列表

主要依赖：
- Flask
- Flask-SocketIO
- requests (用于API调用)
- protobuf (用于直播协议)

### 可选依赖

- LLMX API密钥（用于AI功能）
- Node.js（用于某些JavaScript工具）

## 运行说明

### 通过平台运行（推荐）

游戏后端会自动被平台加载：

```bash
cd MaxGamer/backend
python app.py
```

平台会自动：
1. 扫描GameLibrary/games目录
2. 加载fortune-game的后端
3. 注册所有API端点
4. 初始化服务

### 独立运行（开发测试）

如果需要独立测试游戏后端：

```bash
cd GameLibrary/games/fortune-game/backend
python app.py
```

## 故障排除

### AI功能不可用

**症状**: API返回 `ai_enabled: false`

**原因**: 
- LLMX API密钥未配置
- 依赖包未安装
- 网络连接问题

**解决**:
1. 配置API密钥
2. 安装依赖: `pip install -r requirements.txt`
3. 检查网络连接

### 直播功能不可用

**症状**: API返回 `live_enabled: false`

**原因**:
- 直播服务依赖未安装
- protobuf未正确配置

**解决**:
1. 安装依赖
2. 检查protobuf编译
3. 验证直播间ID

### 导入错误

**症状**: 模块导入失败

**解决**:
1. 确保在正确的目录运行
2. 检查Python路径配置
3. 重新安装依赖

## 开发建议

1. **本地开发**: 使用独立运行模式测试
2. **集成测试**: 通过平台运行验证集成
3. **日志调试**: 查看控制台输出了解服务状态
4. **渐进式开发**: 先确保基础功能，再添加高级特性

## 总结

- ✅ Pylance警告是正常的，不影响运行
- ✅ 代码实现了完整的错误处理和降级机制
- ✅ 所有功能都可以独立启用/禁用
- ✅ 支持开发和生产两种运行模式

如有问题，请查看控制台日志或参考文档。