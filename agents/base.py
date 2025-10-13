from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Abstract base class for all agents."""

    @abstractmethod
    def execute(self, task: str, **kwargs) -> str:
        """
        Executes a given task and returns the result.

        Args:
            task: The task to be performed by the agent.
            **kwargs: Additional arguments for the agent.

        Returns:
            A string containing the result of the task execution.
        """
        pass