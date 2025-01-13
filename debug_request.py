# -*- coding: utf-8 -*-
"""Debug script for testing model API endpoints."""
import requests
from loguru import logger


def test_degpt() -> None:
    """Test the DeGPT model endpoint with a simple greeting."""
    payload = {
        "model_type": "degpt",
        "config_name": "degpt_test",
        "input": "Hello! Please introduce yourself.",
        "stream": False,
    }

    try:
        print("\nTesting DeGPT model...")
        response = requests.post(
            "http://localhost:5000/api/models/test",
            json=payload,
            timeout=30,
        )
        print(f"Status Code: {response.status_code}")
        print("Response:", response.text)
    except Exception as e:
        logger.error("DeGPT request failed: %s", str(e))


def test_superimage() -> None:
    """Test the Superimage model endpoint with a landscape prompt."""
    payload = {
        "model_type": "superimage",
        "config_name": "superimage_test",
        "input": "A beautiful sunset over mountains",
        "parameters": {
            # This will trigger auth error as expected
            "auth_token": "test_token",
        },
        "stream": False,
    }

    try:
        print("\nTesting Superimage model...")
        response = requests.post(
            "http://localhost:5000/api/models/test",
            json=payload,
            timeout=30,
        )
        print(f"Status Code: {response.status_code}")
        print("Response:", response.text)
    except Exception as e:
        logger.error("Superimage request failed: %s", str(e))


if __name__ == "__main__":
    test_degpt()
    test_superimage()
