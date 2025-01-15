from multiprocessing import freeze_support
from agentscope.server import RpcAgentServerLauncher

def main():
    server = RpcAgentServerLauncher(
        host="localhost",
        port=8888,
        server_id="test_server1",
        capacity=32,
        local_mode=True,
        studio_url="http://127.0.0.1:5000",  # 可选：连接到Studio
        json_args={
            "project": "DecentralGPT",  # 添加project字段
        }
    )
    server.launch(in_subprocess=True)

if __name__ == "__main__":
    freeze_support()
    main()