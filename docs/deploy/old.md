# AgentScope 部署教程

本教程将指导您如何在Ubuntu服务器上部署AgentScope项目。

## 目录
- [1. 环境准备](#1-环境准备)
- [2. 项目安装](#2-项目安装)
- [3. 项目配置](#3-项目配置)
- [4. 服务部署](#4-服务部署)
- [5. 系统服务配置](#5-系统服务配置)
- [6. 服务管理](#6-服务管理)
- [7. 日志管理](#7-日志管理)

## 1. 环境准备

### 1.1 系统依赖安装
```bash
# 更新系统包
sudo apt update
sudo apt install python3.9 python3.9-venv python3-pip

# 安装Redis(如果需要使用分布式功能)
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### 1.2 Python环境配置
```bash
# 创建虚拟环境
python3.9 -m venv agentscope_env

# 激活虚拟环境
source agentscope_env/bin/activate
```

## 2. 项目安装

### 2.1 获取代码
```bash
# 克隆代码
git clone https://github.com/modelscope/agentscope.git
cd agentscope
```

### 2.2 安装依赖
根据需求选择以下安装方式之一：
```bash
# 基础安装
pip install -e .

# 完整安装(包含所有功能)
pip install -e ".[full]"

# 在线部署安装(包含gunicorn等生产环境需要的包)
pip install -e ".[online]"
```

## 3. 项目配置

### 3.1 目录结构
```bash
项目目录/
├── logs/                    # 日志根目录
│   ├── server/             # 服务器日志
│   │   ├── access.log      # 访问日志
│   │   └── error.log       # 错误日志
│   ├── agents/             # Agent日志
│   │   └── agent_*.log     # 各个Agent的日志
│   └── studio/             # Studio日志
│       ├── access.log      # Studio访问日志
│       └── error.log       # Studio错误日志
└── configs/                # 配置文件目录
    └── model_configs.json  # 模型配置文件
```

### 3.2 创建必要目录
```bash
# 创建日志目录
mkdir -p logs/{server,agents,studio}

# 创建配置目录
mkdir -p configs
```

### 3.3 配置模型
创建 `configs/model_configs.json`：
```json
{
    "openai": {
        "api_key": "your-api-key",
        "model": "gpt-3.5-turbo"
    }
    // 其他模型配置...
}
```

## 4. 服务部署

### 4.1 基础部署
```bash
# 启动AgentScope Server
as_server start --host 0.0.0.0 --port 12310 \
    --model-config-path configs/model_configs.json \
    --local-mode false
```

### 4.2 分布式部署（使用Redis）
```bash
# 启动AgentScope Server
as_server start --host 0.0.0.0 --port 12310 \
    --pool-type redis \
    --redis-url redis://localhost:6379 \
    --model-config-path configs/model_configs.json \
    --local-mode false \
    --capacity 32 \
    --max-pool-size 8192
```

### 4.3 Studio服务部署
```bash
# 使用gunicorn启动Studio服务
gunicorn -w 4 -b 0.0.0.0:5000 \
    --access-logfile logs/studio/access.log \
    --error-logfile logs/studio/error.log \
    'agentscope.studio:create_app()'
```

## 5. 系统服务配置

### 5.1 AgentScope Server服务
创建文件 `/etc/systemd/system/agentscope-server.service`：
```ini
[Unit]
Description=AgentScope Server
After=network.target

[Service]
Type=simple
User=ubuntu
Environment=PATH=/home/ubuntu/agentscope_env/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
WorkingDirectory=/path/to/agentscope
ExecStart=/home/ubuntu/agentscope_env/bin/as_server start \
    --host 0.0.0.0 \
    --port 12310 \
    --model-config-path configs/model_configs.json \
    --local-mode false
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5.2 Studio服务
创建文件 `/etc/systemd/system/agentscope-studio.service`：
```ini
[Unit]
Description=AgentScope Studio
After=network.target

[Service]
Type=simple
User=ubuntu
Environment=PATH=/home/ubuntu/agentscope_env/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
WorkingDirectory=/path/to/agentscope
ExecStart=/home/ubuntu/agentscope_env/bin/gunicorn \
    --workers 4 \
    --bind 0.0.0.0:5000 \
    --access-logfile logs/studio/access.log \
    --error-logfile logs/studio/error.log \
    'agentscope.studio:create_app()'
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5.3 启用服务
```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启动并启用服务
sudo systemctl start agentscope-server
sudo systemctl start agentscope-studio
sudo systemctl enable agentscope-server
sudo systemctl enable agentscope-studio
```

## 6. 服务管理

为了方便管理服务，创建管理脚本 `scripts/service/manage.sh`：

```bash
#!/bin/bash

# 服务名称
SERVICES=("agentscope-server" "agentscope-studio")

# 显示用法
usage() {
    echo "用法: $0 {start|stop|restart|status|enable|disable|logs} [service_name]"
    echo "service_name可选值: server, studio, all(默认)"
    echo "例子:"
    echo "  $0 start          # 启动所有服务"
    echo "  $0 start server   # 只启动server服务"
    echo "  $0 status studio  # 查看studio服务状态"
    echo "  $0 logs server    # 查看server服务日志"
}

# 获取服务名称
get_service_name() {
    local service=$1
    case $service in
        server)
            echo "agentscope-server"
            ;;
        studio)
            echo "agentscope-studio"
            ;;
        *)
            echo ""
            ;;
    esac
}

# 执行命令
execute_command() {
    local command=$1
    local service=$2
    
    if [ "$service" = "all" ] || [ -z "$service" ]; then
        for svc in "${SERVICES[@]}"; do
            echo "执行: $command $svc"
            sudo systemctl $command $svc
        done
    else
        local service_name=$(get_service_name $service)
        if [ -n "$service_name" ]; then
            echo "执行: $command $service_name"
            sudo systemctl $command $service_name
        else
            echo "错误: 未知的服务 '$service'"
            usage
            exit 1
        fi
    fi
}

# 查看日志
view_logs() {
    local service=$1
    if [ "$service" = "all" ] || [ -z "$service" ]; then
        echo "错误: 查看日志时必须指定具体服务"
        usage
        exit 1
    else
        local service_name=$(get_service_name $service)
        if [ -n "$service_name" ]; then
            sudo journalctl -u $service_name -f
        else
            echo "错误: 未知的服务 '$service'"
            usage
            exit 1
        fi
    fi
}

# 主逻辑
case "$1" in
    start|stop|restart|status|enable|disable)
        execute_command $1 $2
        ;;
    logs)
        view_logs $2
        ;;
    *)
        usage
        exit 1
        ;;
esac
```

使用管理脚本：
```bash
# 添加执行权限
chmod +x scripts/service/manage.sh

# 常用命令
./scripts/service/manage.sh start        # 启动所有服务
./scripts/service/manage.sh stop server  # 停止server服务
./scripts/service/manage.sh restart      # 重启所有服务
./scripts/service/manage.sh status       # 查看所有服务状态
./scripts/service/manage.sh logs studio  # 查看studio服务日志
```

## 7. 日志管理

### 7.1 日志轮转配置
创建文件 `/etc/logrotate.d/agentscope`：
```
/path/to/agentscope/logs/*/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 ubuntu ubuntu
}
```

### 7.2 查看日志
```bash
# 使用管理脚本查看实时日志
./scripts/service/manage.sh logs server
./scripts/service/manage.sh logs studio

# 直接查看日志文件
tail -f logs/server/error.log
tail -f logs/studio/access.log
```

## 补充说明

### 关于Redis的使用
即使在单机部署时，Redis也提供了重要的功能：
- 提供可靠的消息队列
- 支持多进程间的数据共享和通信
- 提供数据持久化
- 可以缓存常用数据，提高性能
- 为后续扩展到多机部署做准备

### 关于Gunicorn和Systemd
- Gunicorn负责：
  - 处理HTTP请求
  - 管理工作进程
  - 进程间负载均衡
  - 处理请求超时
  - 优雅重启

- Systemd负责：
  - 开机自动启动gunicorn
  - 如果gunicorn崩溃，自动重启
  - 收集gunicorn的日志
  - 提供统一的管理接口

两者配合提供了完整的生产环境部署方案。 