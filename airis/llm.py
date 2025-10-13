from langchain_anthropic import ChatAnthropic
from airis.config import config
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

class LLMClient:
    def __init__(self):
        llm_provider = config.get("llm.provider", "anthropic")
        model_name = config.get("llm.model_name", "claude-3-sonnet-20240229")
        api_key = os.environ.get("ANTHROPIC_API_KEY") or config.get("llm.api_key")

        if not api_key:
            raise ValueError("API key for LLM not found. Please set it in config.yaml or as an environment variable.")

        if llm_provider == "anthropic":
            self.client = ChatAnthropic(
                model=model_name, 
                api_key=api_key,
                max_tokens=4000,  # Reduce max tokens to avoid rate limits
                temperature=0.1   # Lower temperature for more consistent output
            )
        else:
            # This can be extended to support other providers like OpenAI, etc.
            raise NotImplementedError(f"LLM provider '{llm_provider}' is not currently supported.")

    def invoke(self, prompt: str):
        """Sends a prompt to the LLM and returns the response."""
        return self.client.invoke(prompt)

# Singleton instance
llm_client = LLMClient()