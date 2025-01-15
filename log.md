```js
fetch('http://127.0.0.1:5000/convert-to-py-and-run', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        data: JSON.stringify({
            "2": {
                "data": {
                    "args": {
                        "config_name": "degpt",
                        "model_type": "degpt_chat",  // 改为 degpt_chat
                        "api_url": "https://korea-chat.degpt.ai/api/v0/chat/completion/proxy",
                        "model_name": "Llama3.3-70B",
                        "json_args": {
                            "model": "Llama3.3-70B",
                            "project": "DecentralGPT",
                            "stream": false
                        }
                    }
                },
                "inputs": {},
                "name": "post_api_chat",
                "outputs": {}
            },
            "3": {
                "data": {
                    "args": {
                        "name": "User"
                    }
                },
                "inputs": {
                    "input_1": {
                        "connections": []
                    }
                },
                "name": "UserAgent",
                "outputs": {
                    "output_1": {
                        "connections": [
                            {
                                "node": "4",
                                "output": "input_1"
                            }
                        ]
                    }
                }
            },
            "4": {
                "data": {
                    "args": {
                        "model_config_name": "degpt",  // 对应上面的 config_name
                        "name": "Assistant",
                        "sys_prompt": "You are an assistant"
                    }
                },
                "inputs": {
                    "input_1": {
                        "connections": [
                            {
                                "input": "output_1",
                                "node": "3"
                            }
                        ]
                    }
                },
                "name": "DialogAgent",
                "outputs": {
                    "output_1": {
                        "connections": []
                    }
                }
            }
        }, null, 4)
    })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error('Error:', error));

```









```py
import agentscope
from agentscope.manager import ModelManager
from agentscope.agents import UserAgent, DialogAgent
from typing import Optional, Dict, Any

def initialize_model_config() -> Dict[str, Any]:
    """初始化模型配置"""
    return {
        "config_name": "degpt",
        "model_type": "post_api_chat",
        "api_url": "https://korea-chat.degpt.ai/api/v0/chat/completion/proxy",
        "model_name": "Llama3.3-70B",
        "json_args": {
            "model": "Llama3.3-70B",
            "project": "DecentralGPT",
            "stream": False,
        }
    }

def setup_agentscope(runtime_id: str) -> None:
    """初始化AgentScope环境"""
    agentscope.init(
        logger_level="DEBUG",
        runtime_id=runtime_id,
        studio_url="http://127.0.0.1:5000",
    )
    ModelManager.get_instance().load_model_configs([initialize_model_config()])

def create_conversation_flow() -> Optional[Any]:
    """创建会话流程"""
    flow = None
    user_agent = UserAgent(name="User")
    assistant_agent = DialogAgent(
        model_config_name="degpt", 
        name="Assistant", 
        sys_prompt="You are an assistant"
    )

    flow = user_agent(flow)
    return assistant_agent(flow)

def main() -> None:
    runtime_id = "run_20250114-200854_bnjcbn"
    setup_agentscope(runtime_id)
    create_conversation_flow()

if __name__ == "__main__":
    main()

```