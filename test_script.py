# -*- coding: utf-8 -*-
"""Test script for running AgentScope with model configurations."""
import time
from typing import NoReturn
import agentscope
from agentscope.manager import ModelManager


def main() -> NoReturn:
    """Initialize AgentScope with model configurations for testing.

    This script loads model configurations and keeps running to maintain
    the server process. It runs indefinitely until interrupted.
    """
    # Initialize AgentScope
    agentscope.init()

    # Initialize model configs
    model_manager = ModelManager.get_instance()
    model_configs = [
        {
            "config_name": "degpt_test",
            "model_type": "degpt_chat",
            "model_name": "DeepSeek-V3",
            "api_url": "https://api.degpt.ai/v1/chat/completions",
            "stream": False,
            "headers": {
                "accept": "*/*",
                "accept-language": "zh-CN,zh;q=0.9",
                "content-type": "application/json",
                "sec-ch-ua": (
                    '"Google Chrome";v="131", "Chromium";v="131", '
                    '"Not_A Brand";v="24"'
                ),
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"macOS"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
            },
        },
        {
            "config_name": "superimage_test",
            "model_type": "superimage_generation",
            "model_name": "flux",
            "api_url": (
                "https://test.superimage.ai/api/v1/prompts/generate-image"
            ),
        },
    ]
    model_manager.load_model_configs(model_configs)

    # Keep the script running
    while True:
        time.sleep(1)
