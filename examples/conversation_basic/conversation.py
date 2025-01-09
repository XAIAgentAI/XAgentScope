# -*- coding: utf-8 -*-
"""A simple example for conversation between user and assistant agent."""
import agentscope
from agentscope.agents import DialogAgent
from agentscope.agents.user_agent import UserAgent
from agentscope.pipelines.functional import sequentialpipeline


def main() -> None:
    """A basic conversation demo"""

    # Initialize AgentScope with Ollama model config
    import json

    with open("../../configs/ollama_config.json", "r") as f:
        ollama_config = json.load(f)

    agentscope.init(
        model_configs=[ollama_config],
        project="Multi-Agent Conversation",
        save_api_invoke=False,  # Disable API call recording to avoid serialization issues
    )

    # Init two agents
    dialog_agent = DialogAgent(
        name="Assistant",
        sys_prompt="You're a helpful assistant.",
        model_config_name="my_ollama_chat_config",  # using our Ollama model
    )
    user_agent = UserAgent()

    # start the conversation between user and assistant
    x = None
    while x is None or x.content != "exit":
        x = sequentialpipeline([dialog_agent, user_agent], x)


if __name__ == "__main__":
    main()
