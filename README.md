# XAgentScope项目结构与服务说明

## 一、项目文件结构

### 核心目录结构
```
/XAgentScope/
├── src/agentscope/          # 核心实现
│   ├── agents/             # 智能体实现
│   ├── models/             # 模型API封装
│   ├── service/            # 工具服务
│   ├── memory/             # 内存管理
│   ├── rpc/               # 分布式计算
│   └── web/               # Web交互工具
├── examples/               # 示例应用
├── docs/                   # 文档
├── tests/                  # 单元测试
└── scripts/                # 模型API启动脚本
```

## 二、模块功能说明

### 1. 核心模块
- **agents**: 实现各类智能体
  - dialog_agent.py: 对话智能体
  - react_agent.py: ReAct模式智能体
  - rag_agent.py: 检索增强智能体
  - user_agent.py: 用户交互智能体

- **models**: 支持多种模型API
  - OpenAI模型接口
  - DashScope模型接口
  - Gemini模型接口
  - ZhipuAI模型接口
  - Ollama模型接口等

- **service**: 提供多种服务工具
  - web/: 网络服务(搜索、维基等)
  - browser/: 浏览器控制
  - sql_query/: 数据库查询
  - execute_code/: 代码执行
  - multi_modality/: 多模态处理

### 2. 扩展功能
- **memory**: 智能体记忆管理
- **rpc**: 分布式计算支持
- **web**: Web界面和交互工具

## 三、可用服务

### 1. 前端服务
1. AgentScope Studio (Web界面)
   - Dashboard: 监控运行应用
   - Workstation: 拖拽式构建应用
   - Server Manager: 分布式服务管理

2. Web浏览器服务
   - 支持网页交互
   - 支持可视化操作

### 2. 后端服务
1. 模型服务
   - 本地模型API服务
     - Ollama服务
     - Flask-based服务
     - FastChat服务
     - vllm服务
   - 远程模型API
     - OpenAI API
     - DashScope API
     - 其他云服务API

2. 分布式服务
   - 支持单机多进程
   - RPC服务器
   - 分布式对话系统

## 四、服务启动方法

### 1. 基础安装
```bash
# 创建Python环境（推荐Python 3.9+）
conda create -n agentscope python=3.9
conda activate agentscope

# 安装AgentScope
git clone https://github.com/modelscope/agentscope.git
cd agentscope
pip install -e .

# 安装额外依赖（按需选择）
pip install agentscope[service]     # 服务组件
pip install agentscope[distribute]  # 分布式支持
pip install agentscope[full]        # 完整安装
```

### 2. 启动AgentScope Studio
```python
import agentscope

# 启动Studio服务
agentscope.studio.init(
    host="127.0.0.1",
    port=5000,
    run_dirs=["path/to/runs"]  # 可选：指定运行历史目录
)
```
访问 http://127.0.0.1:5000 使用Web界面

### 3. 启动模型服务
根据需要选择以下方式之一：

1. Ollama服务
```bash
# 安装Ollama
ollama pull llama2  # 示例模型

# 配置模型
{
    "config_name": "my_ollama_chat",
    "model_type": "ollama_chat",
    "model_name": "llama2"
}
```

2. Flask服务
```bash
# 安装依赖
pip install flask torch transformers accelerate

# 启动服务
python flask_transformers/setup_hf_service.py \
    --model_name_or_path meta-llama/Llama-2-7b-chat-hf \
    --device "cuda:0" \
    --port 8000
```

### 4. 启动分布式服务
```bash
# 启动助手节点
python distributed_dialog.py --role assistant --assistant-host localhost --assistant-port 12010

# 启动用户节点
python distributed_dialog.py --role user --assistant-host localhost --assistant-port 12010
```

### 5. 启动Web浏览器服务
```bash
# 安装依赖
pip install playwright
playwright install

# 在代码中使用
from agentscope.service import WebBrowser
browser = WebBrowser()
```

## 注意事项
1. 运行应用程序和AgentScope Studio需要在同一台机器上
2. 分布式模式目前支持单机多进程，多机多进程支持在开发中
3. 建议从源码安装以获取最新功能
4. Web浏览器服务仍处于测试阶段，功能会持续更新





问题：
1。 多个交互方式的不同。难易程度，优缺点。
2。 目前前端服务是如何和后端服务进行交互的。我如果想要改成前端用react的话。对应的启动web浏览器服务，这个能力是需要修改的。因为它依赖于客户端嘛。那我目前已有的利用Python对接playwright这套逻辑代码是不是就不可以复用了？其他还有没有类似的这种情况导致我可能使用纯前端框架。会有成本。那这样子的话，我是不是需要考虑保留python项目中写的前端代码。但是Python写的前端代码，它的能力。会有所欠缺，它的组件库什么的没有办法很好的使用。


技术栈选型？技术架构方案？







三条路：
1. python前端。能复用的模块就是工作台
2. react前端。能复用的模块是
3. svelte前端。能复用的模块是 对话




原型图：
https://modao.cc/proto/zX3BvGh5sp71v3pVGHngL/sharing?view_mode=read_only&screen=rbpUYEfU83FsMGOPq