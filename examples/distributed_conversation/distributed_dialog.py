# -*- coding: utf-8 -*-
""" An example of distributed dialog """

import os
import sys
import json
import errno
import select
import argparse
from typing import Any, Optional, Union, Dict
from loguru import logger

# Configure UTF-8 encoding for all I/O
import io
import locale
import codecs
import fcntl
import termios


# Ensure proper encoding for all I/O operations
def setup_io_encoding():
    """Configure proper encoding for stdin/stdout/stderr"""
    import os
    import locale
    import sys
    import io

    # Set basic UTF-8 environment
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["LANG"] = "C.UTF-8"
    os.environ["LC_ALL"] = "C.UTF-8"

    # Configure I/O streams with UTF-8 encoding
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer,
            encoding="utf-8",
            errors="replace",
            line_buffering=True,
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer,
            encoding="utf-8",
            errors="replace",
            line_buffering=True,
        )
        sys.stdin = io.TextIOWrapper(
            sys.stdin.buffer,
            encoding="utf-8",
            errors="replace",
            line_buffering=True,
        )

    # Configure logging with UTF-8 support
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        encoding="utf-8",
    )

    # Set basic locale
    try:
        locale.setlocale(locale.LC_ALL, "C.UTF-8")
    except locale.Error:
        pass


# Set up encoding at module import
setup_io_encoding()

import agentscope
from agentscope.agents.user_agent import UserAgent
from agentscope.agents.dialog_agent import DialogAgent
from agentscope.server import RpcAgentServerLauncher
from agentscope.message import Msg
from agentscope.rpc.rpc_config import DistConf


def load_model_config(config_path: str) -> Dict:
    """Load model configuration from JSON file."""
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        # Ensure config is in list format as required by agentscope.init()
        return [config] if isinstance(config, dict) else config


def parse_args() -> argparse.Namespace:
    """Parse arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--role",
        choices=["assistant", "user"],
        default="user",
    )
    parser.add_argument(
        "--assistant-port",
        type=int,
        default=12010,
    )
    parser.add_argument(
        "--assistant-host",
        type=str,
        default="localhost",
    )
    return parser.parse_args()


def setup_assistant_server(assistant_host: str, assistant_port: int) -> None:
    """Set up assistant rpc server with detailed error handling"""
    try:
        # Load model configuration with verbose logging
        logger.info("Loading model configuration...")
        config_path = "../../configs/ollama_config.json"
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        model_configs = load_model_config(config_path)
        logger.info(f"Loaded model config: {model_configs}")

        # Initialize AgentScope
        logger.info("Initializing AgentScope...")
        agentscope.init(
            model_configs=model_configs,
            project="Distributed Conversation",
            save_api_invoke=False,
        )
        logger.info("AgentScope initialized successfully")

        # Create dialog agent
        logger.info("Creating dialog agent...")
        kwargs = {
            "name": "助手",
            "sys_prompt": model_configs[0]["options"].get(
                "system",
                "你是一个中文AI助手。",
            ),
            "model_config_name": model_configs[0]["config_name"],
            "use_memory": True,
        }
        try:
            dialog_agent = DialogAgent(**kwargs)
            logger.info("Dialog agent created successfully")
        except Exception as e:
            logger.error(f"Failed to create dialog agent: {e}")
            raise

        # Launch RPC server
        logger.info(
            f"Launching RPC server at {assistant_host}:{assistant_port}...",
        )
        try:
            server = RpcAgentServerLauncher(
                host=assistant_host,
                port=assistant_port,
                custom_agent_classes=[DialogAgent],
                capacity=4,
                local_mode=True,
            )
            logger.info("RPC server created, starting...")
            server.launch(in_subprocess=False)
            logger.info("RPC server launched successfully")
            server.wait_until_terminate()
        except Exception as e:
            logger.error(f"Failed to launch RPC server: {e}")
            raise

    except Exception as e:
        logger.error(f"Critical error in setup_assistant_server: {str(e)}")
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        raise


def print_msg(msg: Any) -> None:
    """Print message with proper encoding handling"""
    try:
        # Get message content with proper encoding
        def get_msg_content(m: Any) -> str:
            if hasattr(m, "result"):  # Handle AsyncResult
                result = m.result()
                return get_msg_content(result)
            elif isinstance(m, Msg):
                return m.formatted_str(colored=True)
            else:
                return str(m)

        # Get properly encoded content
        content = get_msg_content(msg)

        # Ensure content is valid UTF-8
        try:
            # First try to encode as UTF-8 to catch any encoding issues
            encoded_content = content.encode("utf-8", errors="replace")
            # Then decode back to string to ensure it's valid
            decoded_content = encoded_content.decode("utf-8", errors="replace")

            # Print using direct buffer write for consistent output
            if hasattr(sys.stdout, "buffer"):
                sys.stdout.buffer.write(encoded_content)
                sys.stdout.buffer.write(b"\n")
                sys.stdout.buffer.flush()
            else:
                # Fallback to regular print with explicit encoding
                print(decoded_content, flush=True)

            # Log successful message handling
            logger.debug(f"Successfully printed message of type {type(msg)}")

            # Log message if it's a Msg instance
            if isinstance(msg, Msg):
                logger.chat(msg)

        except (UnicodeError, IOError) as e:
            logger.error(f"Encoding error while printing message: {e}")
            # Try fallback encoding
            print(
                content.encode("utf-8", errors="replace").decode(
                    "utf-8",
                    errors="replace",
                ),
                flush=True,
            )

    except Exception as e:
        logger.error(f"Failed to process message: {e}")
        print(
            "<Message content cannot be displayed - encoding error>",
            flush=True,
        )


def run_main_process(assistant_host: str, assistant_port: int) -> None:
    """Run dialog main process with proper encoding handling"""
    try:
        # Load and initialize model configuration
        model_configs = load_model_config("../../configs/ollama_config.json")
        agentscope.init(
            model_configs=model_configs,
            project="Distributed Conversation",
            save_api_invoke=False,  # Disable API call recording to avoid serialization issues
        )

        # Create distributed agent using kwargs dict to match RpcMeta.__call__ expectations
        kwargs = {
            "name": "助手",  # Chinese name for better display
            "sys_prompt": model_configs[0]["options"][
                "system"
            ],  # Use system prompt from config
            "model_config_name": model_configs[0]["config_name"],
            "use_memory": True,
            "to_dist": {
                "host": assistant_host,
                "port": assistant_port,
                "local_mode": True,
                "max_timeout_seconds": 120,  # Match the model timeout
            },
        }
        assistant_agent = DialogAgent(**kwargs)

        # Create local user agent (no RPC needed)
        user_agent = UserAgent(
            name="用户",
            require_url=False,
        )

        logger.info(
            "系统启动成功！开始对话吧！(输入 'exit' 结束对话)",
        )

        # Start conversation loop
        msg = user_agent()
        while not msg.content.endswith("exit"):
            msg = assistant_agent(msg)
            print_msg(msg)
            msg = user_agent(msg)

    except Exception as e:
        logger.error(f"Failed to run main process: {e}")
        raise


if __name__ == "__main__":
    args = parse_args()
    if args.role == "assistant":
        setup_assistant_server(args.assistant_host, args.assistant_port)
    elif args.role == "user":
        run_main_process(args.assistant_host, args.assistant_port)
