"""
LLM Client

Unified LLM client that uses ai_factory for all AI operations.
All AI usage is controlled by config.yaml.
"""

from airis.ai_factory import UnifiedAIClient

# Backward compatibility: LLMClient now uses UnifiedAIClient
class LLMClient:
    """
    LLM Client that respects config.yaml settings.
    Uses ai_factory to create the appropriate AI client.
    """
    
    def __init__(self, task_type: str = "orchestration"):
        """
        Initialize LLM client for specified task type.
        
        Args:
            task_type: Type of task (orchestration, interactive_mode, validation, etc.)
        """
        self.unified_client = UnifiedAIClient(task_type)
    
    def invoke(self, prompt: str):
        """
        Sends a prompt to the configured AI and returns the response.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Response object with .content attribute
        """
        return self.unified_client.invoke(prompt)
    
    def get_engine_name(self) -> str:
        """Get the name of the current engine."""
        return self.unified_client.get_engine_name()


# Singleton instance (for backward compatibility)
llm_client = LLMClient("orchestration")
