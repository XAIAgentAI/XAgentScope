import agentscope

# 开发模式，支持热更新
agentscope.studio.init(
    host="127.0.0.1",
    port=5000,
    debug=True,  # 开启debug模式
    run_dirs=["path/to/runs"]  # 可选：指定运行历史目录
)