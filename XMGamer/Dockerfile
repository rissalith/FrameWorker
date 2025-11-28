# ============================================
# XMGamer 平台 API - Dockerfile
# Python Flask 后端服务
# ============================================

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 配置国内镜像源（阿里云）
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources || \
    sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list || true

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY backend/requirements.txt .

# 配置 pip 使用国内镜像源（阿里云）
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set install.trusted-host mirrors.aliyun.com

# 安装 Python 依赖（分步安装以便调试）
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir Flask==3.0.0 Flask-Cors==4.0.0 && \
    pip install --no-cache-dir Flask-SocketIO==5.3.5 python-socketio==5.10.0 && \
    pip install --no-cache-dir SQLAlchemy==2.0.23 Flask-SQLAlchemy==3.1.1 && \
    pip install --no-cache-dir Flask-JWT-Extended==4.6.0 bcrypt==4.1.2 && \
    pip install --no-cache-dir python-dotenv==1.0.0 requests==2.31.0 && \
    pip install --no-cache-dir sendgrid>=6.11.0 PySocks>=1.7.1 && \
    pip install --no-cache-dir alibabacloud-dysmsapi20170525>=2.0.24 alibabacloud-tea-openapi>=0.3.9 alibabacloud-tea-util>=0.3.11 || echo "阿里云SDK安装失败，跳过"

# 复制应用代码
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# 创建日志目录
RUN mkdir -p /app/logs

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 启动命令
CMD ["python", "backend/app.py"]