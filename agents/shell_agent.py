from agents.base import BaseAgent
from airis.llm import llm_client
from airis.sandbox import Sandbox
import os

class ShellAgent(BaseAgent):
    """Agent for generating and executing shell commands."""

    def __init__(self):
        self.sandbox = Sandbox()

    def execute(self, task: str, **kwargs) -> str:
        """
        Generates a shell command based on the task and executes it in a sandbox.
        """
        prompt = f"""Generate a single shell command to accomplish the following task. 
Only output the command, without any explanation or markdown formatting.

Task: {task}
"""
        
        response = llm_client.invoke(prompt)
        command = response.content
        
        working_dir = os.getcwd()
        stdout, stderr, exit_code = self.sandbox.run_command(command, working_dir)

        if exit_code == 0:
            return f"Command executed successfully.\nOutput:\n{stdout}"
        else:
            return f"Command execution failed.\nError:\n{stderr}"