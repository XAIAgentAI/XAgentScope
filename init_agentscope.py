# -*- coding: utf-8 -*-
import agentscope
import json


def init_model_service():
    """Initialize AgentScope with Ollama model configuration."""
    try:
        # Load the model config from JSON file
        with open("configs/ollama_config.json", "r") as f:
            model_config = json.load(f)

        # Initialize AgentScope with the loaded config
        agentscope.init(model_configs=[model_config])
        print("Successfully initialized AgentScope with Ollama model")
        return True
    except Exception as e:
        print(f"Error initializing AgentScope: {e}")
        return False


if __name__ == "__main__":
    init_model_service()
