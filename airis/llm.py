from langchain_anthropic import ChatAnthropic
from airis.config import config
import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

class LLMClient:
    def __init__(self):
        llm_provider = config.get("llm.provider", "anthropic")
        model_name = config.get("llm.model_name", "claude-3-sonnet-20240229")
        max_tokens = config.get("llm.max_tokens", 4000)
        temperature = config.get("llm.temperature", 0.1)
        
        self.provider = llm_provider
        self._is_gemini = False

        if llm_provider == "anthropic":
            api_key = os.environ.get("ANTHROPIC_API_KEY") or config.get("llm.api_key")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found. Please set it in .env file or as an environment variable.")
            
            self.client = ChatAnthropic(
                model=model_name, 
                api_key=api_key,
                max_tokens=max_tokens,
                temperature=temperature
            )
        
        elif llm_provider == "gemini":
            # Use GeminiAgent for Gemini provider
            from agents.gemini_agent import GeminiAgent
            self.client = GeminiAgent()
            self._is_gemini = True
        
        else:
            # This can be extended to support other providers like OpenAI, etc.
            raise NotImplementedError(f"LLM provider '{llm_provider}' is not currently supported.")

    def invoke(self, prompt: str):
        """Sends a prompt to the LLM and returns the response."""
        if self._is_gemini:
            # GeminiAgent returns string directly
            result = self.client.execute(prompt)
            # Wrap in object with .content attribute for compatibility
            class Response:
                def __init__(self, content):
                    self.content = content
            return Response(result)
        else:
            # Anthropic returns AIMessage with .content attribute
            return self.client.invoke(prompt)

# Singleton instance
llm_client = LLMClient()