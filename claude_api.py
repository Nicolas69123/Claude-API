#!/usr/bin/env python3
"""
Claude API Script
Configure your API key and use Claude programmatically
"""

import anthropic
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration - Add your API key here or use environment variable
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "your-api-key-here")

def call_claude(user_message, model="claude-sonnet-4-5-20250929"):
    """
    Call Claude API with a message

    Args:
        user_message: Your prompt/question for Claude
        model: The Claude model to use
    """
    client = anthropic.Anthropic(api_key=API_KEY)

    message = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    return message.content[0].text


def main():
    """Example usage"""

    # Check if API key is configured
    if API_KEY == "your-api-key-here":
        print("⚠️  Please configure your API key first!")
        print("Option 1: Set environment variable: export ANTHROPIC_API_KEY='your-key'")
        print("Option 2: Edit this file and replace 'your-api-key-here' with your actual key")
        print("\nGet your API key at: https://console.anthropic.com/")
        return

    # Example: Call Claude
    print("Calling Claude API...")
    response = call_claude("Hello! Can you help me with Python?")
    print(f"\nClaude's response:\n{response}")


if __name__ == "__main__":
    main()
