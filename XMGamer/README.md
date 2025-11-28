# XMGamer - 直播互动游戏平台

一个基于 Web 的直播互动游戏平台，提供多种有趣的互动游戏体验。

## 功能特性

- 🎮 游戏市场 - 浏览和启动各种互动游戏
- 🔮 巫女占卜游戏 - 神秘的占卜体验
- 📺 直播互动 - 支持直播间实时互动
- 👤 用户认证系统（邮箱、Google OAuth）
- 🎯 多游戏支持 - 可扩展的游戏框架

## 技术栈

- **后端**: Python Flask, Flask-SocketIO
- **前端**: HTML5, CSS3, JavaScript (原生)
- **数据库**: SQLite
- **认证**: JWT, OAuth 2.0
- **实时通信**: WebSocket

## 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd XMGamer
```

2. 安装 Python 依赖
```bash
cd backend
pip install -r requirements.txt
```

3. 配置环境变量
```bash
# 复制 .env.example 为 .env 并配置
cp .env.example .env
```

4. 初始化数据库
```bash
python init_db.py
```

### 启动服务

#### 方法 1: 使用启动脚本（Windows）
```bash
cd backend
start.bat
```

#### 方法 2: 使用 npm 脚本
```bash
npm start
```

#### 方法 3: 直接运行 Python
```bash
cd backend
python app.py
```

### 访问应用

服务启动后，在浏览器中访问：
```
http://localhost:3000
```

登录页面：
```
http://localhost:3000/login.html
```

## 项目结构

```
XMGamer/
├── backend/              # 后端代码
│   ├── app.py           # Flask 应用入口
│   ├── database.py      # 数据库模型
│   ├── routes/          # API 路由
│   ├── utils/           # 工具函数
│   └── requirements.txt # Python 依赖
├── frontend/            # 前端代码
│   ├── index.html       # 主页面（游戏市场）
│   ├── login.html       # 登录页面
│   ├── css/            # 样式文件
│   ├── js/             # JavaScript 文件
│   ├── images/         # 图片资源
│   └── fortune-game/   # 巫女占卜游戏
└── package.json        # 项目配置
```

## 游戏列表

### 巫女占卜
- 神秘的占卜体验
- 支持直播互动
- AI 智能对话
- 多种占卜类型（爱情、事业、健康等）

### 更多游戏
- 敬请期待...

## API 文档

### 认证相关

- `POST /api/auth/send-email` - 发送邮箱验证码
- `POST /api/auth/login-with-email` - 邮箱验证码登录
- `POST /api/auth/login-with-password` - 密码登录
- `GET /api/auth/me` - 获取当前用户信息
- `POST /api/auth/logout` - 退出登录

### 游戏相关

- `POST /api/fortune/chat` - 占卜聊天接口
- `POST /api/fortune/live/start` - 开始监听直播间
- `POST /api/fortune/live/stop` - 停止监听直播间
- `GET /api/fortune/live/status` - 获取直播监听状态

### 历史记录

- `GET /api/history` - 获取历史记录列表
- `POST /api/history` - 创建历史记录
- `DELETE /api/history/:id` - 删除历史记录

## 开发说明

### 后端开发

后端使用 Flask 框架，主要文件：
- `app.py` - 应用入口和配置
- `routes/auth.py` - 认证相关路由
- `routes/history.py` - 历史记录路由
- `database.py` - 数据库模型定义

### 前端开发

前端使用原生 JavaScript，采用模块化设计：
- `js/main.js` - 主入口文件
- `js/modules/` - 功能模块
- `js/modules/router.js` - 路由管理
- `js/modules/authManager.js` - 认证管理

### 添加新游戏

1. 在 `frontend/` 目录下创建游戏文件夹
2. 在 `js/modules/router.js` 中注册游戏
3. 在游戏市场页面添加游戏卡片

## 配置说明

### 环境变量 (.env)

```env
# Flask 配置
SECRET_KEY=your-secret-key
FLASK_ENV=development

# 数据库
DATABASE_URL=sqlite:///xmgamer.db

# JWT
JWT_SECRET_KEY=your-jwt-secret

# OAuth (可选)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# 邮件服务 (可选)
SENDGRID_API_KEY=your-sendgrid-api-key
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过 Issue 联系我们。
