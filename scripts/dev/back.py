from multiprocessing import freeze_support
from agentscope.server import RpcAgentServerLauncher
import time

def main():

    
    server = RpcAgentServerLauncher(
        host="127.0.0.1",  # 改为与 Studio 相同的 host
        port=8888,
        server_id=f"test_server_{int(time.time())}",
        capacity=32,
        local_mode=True,
        studio_url="http://127.0.0.1:5000"
    )
    server.launch(in_subprocess=True)

if __name__ == "__main__":
    freeze_support()
    main()