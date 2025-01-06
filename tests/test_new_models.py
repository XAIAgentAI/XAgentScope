# -*- coding: utf-8 -*-
"""Test script for new model wrappers."""
from agentscope.models.post_model import (
    DegptChatWrapper,
    SuperimageGenerationWrapper,
)
from agentscope.message import Msg


def test_degpt_chat() -> None:
    """Test DegptChatWrapper with a simple greeting.
    中文说明：使用简单问候测试DegptChatWrapper。
    """
    model = DegptChatWrapper(config_name="degpt-test")
    messages = model.format(Msg("user", "你好", role="user"))
    response = model(messages)  # Now accepts List[dict] input
    print("DegptChat Response:", response.text)
    assert response.text is not None
    assert len(response.text) > 0


def test_superimage() -> None:
    """Test SuperimageGenerationWrapper with an image generation prompt.
    中文说明：测试SuperimageGenerationWrapper的图像生成功能。
    """
    try:
        # Initialize model with optional auth token
        auth_token = None  # In production, get from config or environment
        model = SuperimageGenerationWrapper(
            config_name="superimage-test",
            timeout=10,  # 10 second timeout for testing
            auth_token=auth_token,
        )
        prompt = model.format(Msg("user", "画一个女孩", role="user"))
        response = model(prompt)
        print("Superimage URLs:", response.image_urls)
        assert response.image_urls is not None
        assert len(response.image_urls) > 0
    except RuntimeError as e:
        print("Superimage API error:", str(e))
        if "authorization" in str(e).lower():
            print("Note: Superimage API requires authorization token")
        return  # Skip test if API is not accessible
    except Exception as e:
        print(
            "Unexpected error in Superimage test: "
            f"{type(e).__name__}: {str(e)}",
        )
        raise


if __name__ == "__main__":
    print("Testing DegptChatWrapper...")
    test_degpt_chat()
    print("\nTesting Superimage...")
    test_superimage()  # Test image generation with error handling
