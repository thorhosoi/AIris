"""
AI Engine Factory

Creates AI clients based on config.yaml settings.
Ensures all AI usage goes through centralized configuration.
"""

from airis.config import config
import os


class AIFactory:
    """
    Factory for creating AI clients based on configuration.
    All AI usage should go through this factory.
    """
    
    @staticmethod
    def create_llm_client(task_type: str = "orchestration"):
        """
        Create an LLM client for the specified task type.
        
        Args:
            task_type: Type of task (orchestration, interactive_mode, validation, etc.)
            
        Returns:
            AI client instance
        """
        # Get the engine for this task type from config
        engine = config.get(f"ai_engines.task_routing.{task_type}")
        
        if not engine:
            # Fall back to default engine
            engine = config.get("ai_engines.default_engine", "gemini")
        
        # Verify engine is allowed
        allowed_engines = config.get("ai_engines.allowed_engines", [])
        if engine not in allowed_engines:
            raise ValueError(f"Engine '{engine}' is not in allowed_engines list: {allowed_engines}")
        
        return AIFactory._create_client(engine)
    
    @staticmethod
    def _create_client(engine: str):
        """
        Create a client for the specified engine.
        
        Args:
            engine: Engine name (gemini, claude, cursor, etc.)
            
        Returns:
            Client instance
        """
        if engine == "gemini":
            return AIFactory._create_gemini_client()
        
        elif engine == "claude":
            return AIFactory._create_claude_client()
        
        elif engine == "cursor":
            from agents.cursor_agent import CursorAgent
            return CursorAgent()
        
        elif engine == "web_search":
            # web_search is not an LLM engine, it's an action
            # If web_search is requested as LLM, use default engine instead
            return AIFactory._create_gemini_client()
        
        elif engine == "web_browser":
            # web_browser is not an LLM engine, it's an action
            # If web_browser is requested as LLM, use default engine instead
            return AIFactory._create_gemini_client()
        
        elif engine == "local":
            # Local operations don't need an AI client
            return None
        
        else:
            raise NotImplementedError(f"Engine '{engine}' is not implemented")
    
    @staticmethod
    def _create_gemini_client():
        """Create Gemini client."""
        from agents.gemini_agent import GeminiAgent
        return GeminiAgent()
    
    @staticmethod
    def _create_claude_client():
        """Create Claude client."""
        from langchain_anthropic import ChatAnthropic
        from dotenv import load_dotenv
        
        load_dotenv()
        
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. "
                "Please set it in .env file or disable claude in config.yaml"
            )
        
        model_name = config.get("claude.model_name", "claude-sonnet-4-5-20250929")
        max_tokens = config.get("claude.max_tokens", 4000)
        temperature = config.get("claude.temperature", 0.1)
        
        return ChatAnthropic(
            model=model_name,
            api_key=api_key,
            max_tokens=max_tokens,
            temperature=temperature
        )
    
    @staticmethod
    def get_engine_for_task(task_type: str) -> str:
        """
        Get the configured engine name for a task type.
        
        Args:
            task_type: Type of task
            
        Returns:
            Engine name
        """
        engine = config.get(f"ai_engines.task_routing.{task_type}")
        if not engine:
            engine = config.get("ai_engines.default_engine", "gemini")
        return engine


class UnifiedAIClient:
    """
    Unified AI client that works with any configured engine.
    Provides a consistent interface regardless of the underlying AI.
    """
    
    def __init__(self, task_type: str = "orchestration"):
        self.task_type = task_type
        self.engine = AIFactory.get_engine_for_task(task_type)
        self.client = AIFactory.create_llm_client(task_type)
    
    def invoke(self, prompt: str):
        """
        Send a prompt to the AI and get a response.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Response object with .content attribute
        """
        if self.engine in ["gemini", "cursor", "web_search", "web_browser"]:
            # These return string directly
            if hasattr(self.client, 'execute'):
                result = self.client.execute(prompt)
            else:
                result = str(self.client)
            
            # Wrap in response object
            class Response:
                def __init__(self, content):
                    self.content = content
            
            return Response(result)
        
        elif self.engine == "claude":
            # Claude returns AIMessage with .content
            return self.client.invoke(prompt)
        
        elif self.engine == "local":
            # Local operations don't use AI
            raise ValueError("Local engine doesn't support invoke()")
        
        else:
            raise NotImplementedError(f"Engine '{self.engine}' invoke not implemented")
    
    def get_engine_name(self) -> str:
        """Get the name of the current engine."""
        return self.engine


# Singleton instances for common tasks
_orchestration_client = None
_interactive_client = None
_validation_client = None


def get_orchestration_client():
    """Get the AI client for orchestration tasks."""
    global _orchestration_client
    if _orchestration_client is None:
        _orchestration_client = UnifiedAIClient("orchestration")
    return _orchestration_client


def get_interactive_client():
    """Get the AI client for interactive mode."""
    global _interactive_client
    if _interactive_client is None:
        _interactive_client = UnifiedAIClient("interactive_mode")
    return _interactive_client


def get_validation_client():
    """Get the AI client for validation."""
    global _validation_client
    if _validation_client is None:
        _validation_client = UnifiedAIClient("validation")
    return _validation_client

