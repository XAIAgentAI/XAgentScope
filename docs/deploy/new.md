# AgentScope 分布式部署教程

本教程将指导您如何在Ubuntu服务器上进行AgentScope的分布式部署。

## 目录
- [1. 环境检查与准备](#1-环境检查与准备)
- [2. 项目安装](#2-项目安装)
- [3. 项目配置](#3-项目配置)
- [4. 服务启动脚本](#4-服务启动脚本)
- [5. 日志管理](#5-日志管理)

## 1. 环境检查与准备

### 1.1 环境检查
```bash
# 创建检查脚本 scripts/check_env.sh
#!/bin/bash

echo "开始环境检查..."

# 检查Python
python_version=$(python3 -V 2>&1 | awk '{print $2}')
if [ $? -eq 0 ]; then
    echo "✓ 已安装Python: $python_version"
else
    echo "✗ 未安装Python3"
    need_python=true
fi

# 检查pip
pip_version=$(pip3 -V 2>&1 | awk '{print $2}')
if [ $? -eq 0 ]; then
    echo "✓ 已安装pip: $pip_version"
else
    echo "✗ 未安装pip3"
    need_pip=true
fi

# 检查virtualenv
if python3 -m venv --help > /dev/null 2>&1; then
    echo "✓ 已安装venv"
else
    echo "✗ 未安装venv"
    need_venv=true
fi

# 检查Redis
if systemctl status redis-server > /dev/null 2>&1; then
    echo "✓ Redis服务已安装并运行"
else
    if redis-cli --version > /dev/null 2>&1; then
        echo "! Redis已安装但服务未运行"
        need_redis_start=true
    else
        echo "✗ 未安装Redis"
        need_redis=true
    fi
fi

# 安装缺失的包
if [ "$need_python" = true ] || [ "$need_pip" = true ] || [ "$need_venv" = true ] || [ "$need_redis" = true ]; then
    echo "需要安装以下包："
    sudo apt update
    
    [ "$need_python" = true ] && echo "安装Python3..." && sudo apt install -y python3.9
    [ "$need_pip" = true ] && echo "安装pip3..." && sudo apt install -y python3-pip
    [ "$need_venv" = true ] && echo "安装venv..." && sudo apt install -y python3.9-venv
    [ "$need_redis" = true ] && echo "安装Redis..." && sudo apt install -y redis-server
fi

# 启动Redis（如果需要）
if [ "$need_redis_start" = true ]; then
    echo "启动Redis服务..."
    sudo systemctl start redis-server
fi

echo "环境检查完成！"
```

### 1.2 Python环境配置
```bash
# 创建并激活虚拟环境（如果还没有）
python3.9 -m venv agentscope_env
source agentscope_env/bin/activate
```

## 2. 项目安装

### 2.1 获取代码
```bash
# 克隆代码（如果还没有）
git clone https://github.com/XAIAgentAI/XAgentScope.git
cd XAgentScope

# 切换到主分支
git checkout devin/1736497151-add-degpt-superimage
```

### 2.2 安装依赖
```bash
# 安装在线部署版本（包含所有需要的依赖）
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
# 创建目录结构脚本 scripts/init_dirs.sh
#!/bin/bash

# 创建目录
mkdir -p logs/{server,agents,studio}
mkdir -p configs

# 设置权限
chmod -R 755 logs
chmod -R 755 configs

echo "目录结构创建完成！"
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

## 4. 服务启动脚本

### 4.1 创建启动脚本
创建文件 `scripts/start_services.sh`：
```bash
#!/bin/bash

# 默认配置
DEFAULT_SERVER_PORT=12310
DEFAULT_STUDIO_PORT=5000
DEFAULT_REDIS_URL="redis://localhost:6379"
DEFAULT_CONFIG_PATH="configs/model_configs.json"

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --server-port)
            SERVER_PORT="$2"
            shift 2
            ;;
        --studio-port)
            STUDIO_PORT="$2"
            shift 2
            ;;
        --redis-url)
            REDIS_URL="$2"
            shift 2
            ;;
        --config)
            CONFIG_PATH="$2"
            shift 2
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

# 使用默认值
SERVER_PORT=${SERVER_PORT:-$DEFAULT_SERVER_PORT}
STUDIO_PORT=${STUDIO_PORT:-$DEFAULT_STUDIO_PORT}
REDIS_URL=${REDIS_URL:-$DEFAULT_REDIS_URL}
CONFIG_PATH=${CONFIG_PATH:-$DEFAULT_CONFIG_PATH}

# 确保日志目录存在
mkdir -p logs/{server,studio}

# 启动AgentScope Server
echo "启动AgentScope Server..."
as_server start \
    --host 0.0.0.0 \
    --port $SERVER_PORT \
    --pool-type redis \
    --redis-url $REDIS_URL \
    --model-config-path $CONFIG_PATH \
    --local-mode false \
    --capacity 32 \
    --max-pool-size 8192 > logs/server/server.log 2>&1 &

echo "AgentScope Server 正在启动，端口: $SERVER_PORT"

# 启动Studio服务
echo "启动Studio服务..."
gunicorn -w 4 -b 0.0.0.0:$STUDIO_PORT \
    --access-logfile logs/studio/access.log \
    --error-logfile logs/studio/error.log \
    'agentscope.studio:create_app()' > logs/studio/studio.log 2>&1 &

echo "Studio服务正在启动，端口: $STUDIO_PORT"

echo "所有服务启动完成！"
echo "使用 'tail -f logs/server/server.log' 查看Server日志"
echo "使用 'tail -f logs/studio/studio.log' 查看Studio日志"
```

### 4.2 使用启动脚本
```bash
# 添加执行权限
chmod +x scripts/start_services.sh

# 使用默认配置启动
./scripts/start_services.sh

# 或者自定义配置启动
./scripts/start_services.sh \
    --server-port 12345 \
    --studio-port 5001 \
    --redis-url "redis://localhost:6380" \
    --config "configs/custom_config.json"
```

## 5. 日志管理

### 5.1 日志查看
```bash
# 查看Server日志
tail -f logs/server/server.log

# 查看Studio访问日志
tail -f logs/studio/access.log

# 查看Studio错误日志
tail -f logs/studio/error.log
```

### 5.2 日志清理脚本
创建文件 `scripts/clean_logs.sh`：
```bash
#!/bin/bash

# 设置要保留的日志天数
DAYS_TO_KEEP=7

# 清理超过指定天数的日志
find logs -type f -name "*.log" -mtime +$DAYS_TO_KEEP -exec rm {} \;

echo "已清理${DAYS_TO_KEEP}天前的日志文件"
```

## 补充说明

### 关于Redis的使用
在分布式部署中，Redis的作用：
- 提供可靠的消息队列，确保Agent之间的通信
- 支持多进程和多机器之间的数据共享
- 提供数据持久化，防止数据丢失
- 提供分布式锁，协调多个节点的操作
- 支持水平扩展，可以根据需求增加节点

### 快速参考
1. 环境准备：
```bash
./scripts/check_env.sh
```

2. 初始化目录：
```bash
./scripts/init_dirs.sh
```

3. 启动服务：
```bash
./scripts/start_services.sh
```

4. 查看日志：
```bash
tail -f logs/server/server.log  # 查看Server日志
tail -f logs/studio/studio.log  # 查看Studio日志
```

5. 清理日志：
```bash
./scripts/clean_logs.sh
``` 