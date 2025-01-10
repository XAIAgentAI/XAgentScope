"""A simple example for conversation between user and assistant agent using Ollama."""
import agentscope
from agentscope.agents import DialogAgent
from agentscope.agents.user_agent import UserAgent
from agentscope.pipelines.functional import sequentialpipeline

def main() -> None:
    """A basic conversation demo using Ollama model."""
    # Initialize AgentScope with Ollama model config
    agentscope.init(
        model_configs=[{
            "config_name": "my_ollama_chat",
            "model_type": "ollama_chat",
            "model_name": "llama2",
            "options": {
                "temperature": 0.7,
                "seed": 123
            },
            "keep_alive": "5m"
        }],
        project="Basic Ollama Conversation Demo"
    )

    # Init two agents
    dialog_agent = DialogAgent(
        name="Assistant",
        sys_prompt="You are a helpful assistant. Be concise and clear in your responses. When the user types 'exit', politely end the conversation.",
        model_config_name="my_ollama_chat"
    )
    user_agent = UserAgent()

    # Start conversation
    print("\n=== Starting Conversation ===")
    print("Type 'exit' to end the conversation")
    print("===============================\n")
    
    x = None
    while x is None or x.content != "exit":
        try:
            x = sequentialpipeline([dialog_agent, user_agent], x)
        except Exception as e:
            print(f"\nError during conversation: {e}")
            print("Attempting to continue conversation...\n")
            continue
    
    print("\n=== Conversation Ended ===\n")

if __name__ == "__main__":
    main()
