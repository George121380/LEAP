"""
OpenAI API client wrapper for LLM interactions.

This module provides a secure interface to interact with various LLM APIs
including OpenAI GPT models and Deepseek models.
"""

from openai import OpenAI
import time
import tiktoken
import json
import os
from typing import Optional


def count_tokens_tiktoken(query: str, model: str = "gpt-4o") -> int:
    """Count the number of tokens in a query string for a given model."""
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(query)
    return len(tokens)


def load_api_keys() -> dict:
    """
    Load API keys from environment variables or config file.
    
    Returns:
        dict: Dictionary containing API keys
    """
    # Try to load from environment variables first (more secure)
    openai_key = os.getenv("OPENAI_API_KEY")
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    
    if openai_key and deepseek_key:
        return {
            "openai": openai_key,
            "deepseek": deepseek_key
        }
    
    # Fallback to config file (for development only)
    config_paths = [
        "config/api_keys.json",
        "../config/api_keys.json",
        "../../config/api_keys.json"
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            with open(config_path) as f:
                api_config = json.load(f)
                return {
                    "openai": api_config.get("OpenAI_API_Key", ""),
                    "deepseek": api_config.get("Deepseek_API_Key", "")
                }
    
    raise FileNotFoundError(
        "API keys not found. Please set OPENAI_API_KEY and DEEPSEEK_API_KEY "
        "environment variables or create a config/api_keys.json file."
    )


# Load API keys
API_KEYS = load_api_keys()

# Default model configuration
DEFAULT_MODEL = "gpt-4o"

def ask_GPT(system: str, content: str, model: str = DEFAULT_MODEL) -> Optional[str]:
    """
    Send a query to the specified LLM model and get a response.
    
    Args:
        system: System message to set the context
        content: User content/query
        model: Model to use ("gpt-4o", "deepseek", or "thirdparty")
    
    Returns:
        str: The model's response, or None if failed
    """
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            start_time = time.time()
            
            if model == "gpt-4o":
                client = OpenAI(api_key=API_KEYS["openai"])
                completion = client.chat.completions.create(
                    model="gpt-4o-2024-08-06",
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": content}
                    ]
                )
            elif model == "deepseek":
                client = OpenAI(
                    api_key=API_KEYS["deepseek"], 
                    base_url="https://api.deepseek.com"
                )
                completion = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": content},
                    ],
                    stream=False
                )
            else:
                raise ValueError(f"Unsupported model: {model}")
            
            response_time = time.time() - start_time
            # print(f"LLM response time: {response_time:.2f}s")
            
            return completion.choices[0].message.content
            
        except Exception as e:
            retry_count += 1
            print(f"LLM API error (attempt {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                time.sleep(2 ** retry_count)  # Exponential backoff
            
    print("Failed to get LLM response after all retries")
    return None