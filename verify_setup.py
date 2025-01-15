# -*- coding: utf-8 -*-
"""Verify the development environment setup for AgentScope Studio."""


def verify_imports() -> None:
    """Check if all required modules are accessible."""
    print("Verifying development environment setup:")

    # Check if required modules are installed
    try:
        import agentscope

        _ = agentscope.__name__  # Use import to avoid unused warning
        print("✓ AgentScope modules accessible")
    except ImportError as e:
        print("✗ AgentScope import failed:", e)

    print("\nSetup verification complete!")


if __name__ == "__main__":
    verify_imports()
