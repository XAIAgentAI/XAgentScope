from pathlib import Path
from agentscope.studio import init
from agentscope.studio._app import _db, _app

def init_database():
    """初始化数据库"""
    try:
        # 确保缓存目录存在
        cache_dir = Path.home() / ".cache" / "agentscope" / "studio"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 在应用上下文中创建数据库表
        with _app.app_context():
            _db.create_all()
            print("数据库初始化成功")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        raise

def main():
    # 首先初始化数据库
    init_database()
    
    # 初始化 Studio
    init(
        host="127.0.0.1",
        port=5000,
        run_dirs=["./runs"],  # 指定运行记录存储目录
        debug=True  # 开发模式下启用调试
    )

if __name__ == "__main__":
    main() 