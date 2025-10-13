import re
from agents.base import BaseAgent
from airis.llm import llm_client
from airis.sandbox import Sandbox
import os
import ast # Import ast module for syntax checking

class CodeAgent(BaseAgent):
    """Agent for generating and executing Python code."""

    def __init__(self):
        self.sandbox = Sandbox()

    def execute(self, task: str, **kwargs) -> tuple[str, str]:
        """
        Generates Python code, executes it, and returns the result along with the code.
        Includes a retry mechanism for syntax errors.
        """
        max_retries = 3
        last_error = None

        for attempt in range(max_retries):
            prompt = f"""Generate a simple, complete, and syntactically correct Python function for the following task. 
Ensure all function definitions and control flow statements are followed by an indented block. Only output the code, without any explanation or markdown formatting.

Task: {task}
"""
            if attempt > 0:
                prompt += f"\n\nPrevious attempt failed with a syntax error: {last_error}. Please correct the code."
            
            response = llm_client.invoke(prompt)
            code = response.content.strip()
            
            # Check if the code starts with a markdown block delimiter
            if code.startswith("```python"):
                code = code[len("```python"):].lstrip() # Remove "```python" and leading whitespace
            elif code.startswith("```"):
                code = code[len("```"):].lstrip() # Remove "```" and leading whitespace
                
            # Check if the code ends with a markdown block delimiter
            if code.endswith("```"):
                code = code[:-len("```")].rstrip() # Remove "```" and trailing whitespace

            # --- NEW: Post-process to close unterminated triple-quoted strings ---
            # This is a heuristic to fix common LLM errors where docstrings are cut off.
            if code.count('"""') % 2 != 0:
                code += '"""'
            if code.count("'''") % 2 != 0:
                code += "'''"
            # --- END NEW ---

            try:
                compile(code, '<string>', 'exec')
                # If compilation is successful, break the retry loop
                break
            except SyntaxError as e:
                last_error = e
                if attempt == max_retries - 1:
                    return f"Generated code has a persistent syntax error after {max_retries} attempts: {e}", code
                # Continue to next attempt
        else: # This else block executes if the loop completes without a 'break'
            return "Failed to generate syntactically correct code after multiple attempts.", ""

        # Execute code directly in sandbox using python -c
        working_dir = os.getcwd()
        
        # Use base64 encoding to avoid shell escaping issues
        import base64
        encoded_code = base64.b64encode(code.encode('utf-8')).decode('ascii')
        
        python_cmd = f"""python3 -c "
import base64
code = base64.b64decode('{encoded_code}').decode('utf-8')
exec(code)
" """
        
        stdout, stderr, exit_code = self.sandbox.run_command(python_cmd, working_dir)

        if exit_code == 0:
            result = f"Code executed successfully.\nOutput:\n{stdout}"
        else:
            result = f"Code execution failed.\nError:\n{stderr}"
        
        return result, code
