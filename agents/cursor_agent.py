import requests
import os
import subprocess
import json
from airis.config import config
from .base import BaseAgent

class CursorAgent(BaseAgent):
    def __init__(self):
        self.api_url = config.get("cursor_api_url", "http://localhost:5000") # Default Cursor Background Agent URL
        self.api_key = os.environ.get("CURSOR_API_KEY") # Assuming API key is passed via env var
        
        # Try to find Cursor executable
        import shutil
        possible_paths = [
            "cursor",  # If in PATH
            "/Applications/Cursor.app/Contents/Resources/app/bin/cursor",  # macOS
            "/usr/local/bin/cursor",  # Homebrew
            "/opt/homebrew/bin/cursor",  # Apple Silicon Homebrew
        ]
        
        for path in possible_paths:
            if shutil.which(path) or (path.startswith("/") and os.path.exists(path)):
                self.cursor_path = path
                break
        else:
            self.cursor_path = config.get("cursor_path", "cursor")  # Fallback to config

        if not self.api_key:
            print("Warning: CURSOR_API_KEY not found in environment variables. Cursor API calls might fail.")

    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        headers = {"Content-Type": "application/json"}

        url = f"{self.api_url}/{endpoint}"
        try:
            response = requests.request(method, url, json=data, headers=headers)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.ConnectionError:
            print(f"Error: Could not connect to Cursor Background Agent at {self.api_url}. Is Cursor running with the agent enabled?")
            return {"error": "Connection failed"}
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP Error: {e.response.status_code}"}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {"error": str(e)}

    def get_active_file_content(self) -> tuple[str, str]:
        """
        Gets the content of the currently active file in Cursor.
        Returns a tuple of (file_path, content).
        """
        response = self._make_request("GET", "editor/activeFile")
        if response and "filePath" in response and "content" in response:
            return response["filePath"], response["content"]
        return "", ""

    def apply_diff(self, file_path: str, diff_content: str) -> bool:
        """
        Applies a diff to a specified file in Cursor.
        """
        data = {"filePath": file_path, "diff": diff_content}
        response = self._make_request("POST", "editor/applyDiff", data)
        return response and "success" in response and response["success"]

    def insert_text(self, file_path: str, text: str, start_line: int, start_char: int) -> bool:
        """
        Inserts text into a specified file in Cursor at a given position.
        """
        data = {"filePath": file_path, "text": text, "startLine": start_line, "startChar": start_char}
        response = self._make_request("POST", "editor/insertText", data)
        return response and "success" in response and response["success"]

    def get_editor_context(self) -> dict:
        """
        Gets the current editor context, including active file, selection, etc.
        """
        response = self._make_request("GET", "editor/context")
        return response if response else {}
    
    def open_file_in_cursor(self, file_path: str) -> bool:
        """
        Opens a file in Cursor using the CLI.
        """
        try:
            # Try to execute Cursor on the host system
            # This works by running the command through the host's shell
            result = subprocess.run(
                f"open -a Cursor {file_path}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            print(f"Error opening file in Cursor: {e}")
            return False
    
    def get_cursor_version(self) -> str:
        """
        Gets the Cursor version.
        """
        try:
            result = subprocess.run(
                [self.cursor_path, "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip() if result.returncode == 0 else "Unknown"
        except Exception as e:
            return f"Error: {e}"
    
    def _generate_code_with_cursor(self, instruction: str) -> tuple[str, str]:
        """
        Generate code using Cursor's AI capabilities.
        """
        try:
            # Create a temporary file for Cursor to work with
            import tempfile
            import os
            
            # Create a temporary Python file with the instruction
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write("# Generated by Airis via Cursor\n")
                temp_file.write(f"# Task: {instruction}\n\n")
                temp_file.write("# Use Cursor's AI to generate the code\n")
                temp_file.write("# Press Cmd+K to open Cursor's AI chat\n")
                temp_file.write("# Ask: 'Please generate Python code for: " + instruction + "'\n\n")
                temp_file_path = temp_file.name
            
            # Try to open the file in Cursor
            try:
                if self.open_file_in_cursor(temp_file_path):
                    return f"Cursorでファイルを開きました: {temp_file_path}\n\nCursorのAIを使用してコードを生成してください:\n1. Cmd+Kを押してAIチャットを開く\n2. '{instruction}' のコードを生成してください", temp_file_path
                else:
                    # Fallback: create the file and provide instructions
                    return f"ファイルを作成しました: {temp_file_path}\n\nCursorで開いてAIを使用してください:\n1. Cursorでファイルを開く\n2. Cmd+KでAIチャットを開く\n3. '{instruction}' のコードを生成してください", temp_file_path
            except Exception as e:
                # Fallback: create the file and provide instructions
                return f"ファイルを作成しました: {temp_file_path}\n\nCursorで開いてAIを使用してください:\n1. Cursorでファイルを開く\n2. Cmd+KでAIチャットを開く\n3. '{instruction}' のコードを生成してください", temp_file_path
                
        except Exception as e:
            return f"エラー: ファイルの作成に失敗しました - {e}", ""
    
    def _get_cursor_ai_suggestion(self, instruction: str) -> str:
        """
        Get AI suggestion from Cursor for the given instruction.
        """
        try:
            # This would integrate with Cursor's AI API
            # For now, return a placeholder
            return f"Cursor AI提案: {instruction} のコードを生成します。"
        except Exception as e:
            return f"エラー: Cursor AI提案の取得に失敗しました - {e}"
    
    def execute(self, instruction: str, context: str | None = None, **kwargs) -> str:
        """
        Execute Cursor-related operations based on instruction.
        """
        
        instruction_lower = instruction.lower()
        
        # Code generation keywords
        code_keywords = ["code", "python", "program", "script", "function", "class", "write", "create", "generate"]
        
        if any(keyword in instruction_lower for keyword in code_keywords):
            # Generate code using Cursor
            result, file_path = self._generate_code_with_cursor(instruction)
            if file_path:
                return f"{result}\nファイル: {file_path}"
            else:
                return result
        
        elif "open" in instruction_lower or "ファイルを開く" in instruction_lower:
            # Extract file path from instruction
            import re
            file_match = re.search(r'(\S+\.\w+)', instruction)
            if file_match:
                file_path = file_match.group(1)
                if self.open_file_in_cursor(file_path):
                    return f"ファイル '{file_path}' をCursorで開きました。"
                else:
                    return f"エラー: ファイル '{file_path}' をCursorで開けませんでした。"
            else:
                return "エラー: ファイルパスが見つかりません。"
        
        elif "version" in instruction_lower or "バージョン" in instruction_lower:
            version = self.get_cursor_version()
            return f"Cursor バージョン: {version}"
        
        elif "context" in instruction_lower or "コンテキスト" in instruction_lower:
            context = self.get_editor_context()
            return f"エディターコンテキスト: {json.dumps(context, indent=2, ensure_ascii=False)}"
        
        elif "active" in instruction_lower or "アクティブ" in instruction_lower:
            file_path, content = self.get_active_file_content()
            if file_path:
                return f"アクティブファイル: {file_path}\n内容:\n{content[:500]}..."
            else:
                return "アクティブファイルが見つかりません。"
        
        elif "suggest" in instruction_lower or "提案" in instruction_lower:
            suggestion = self._get_cursor_ai_suggestion(instruction)
            return suggestion
        
        else:
            return "利用可能なCursorコマンド: code, open, version, context, active, suggest"
