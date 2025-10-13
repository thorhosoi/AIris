import subprocess
import os
from .base import BaseAgent

class GitAgent(BaseAgent):
    """
    Agent for managing git operations.
    """
    
    def __init__(self):
        pass
    
    def _run_git_command(self, command: str, cwd: str = None) -> tuple[str, str, int]:
        """
        Run a git command and return stdout, stderr, and exit code.
        """
        try:
            # Use shell=True for proper command parsing
            result = subprocess.run(
                command,
                cwd=cwd or os.getcwd(),
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
            )
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except subprocess.TimeoutExpired:
            return "", "Git command timed out", 1
        except Exception as e:
            return "", f"Error running git command: {e}", 1
    
    def _check_git_repo(self, path: str = None) -> bool:
        """
        Check if the current directory is a git repository.
        """
        stdout, stderr, exit_code = self._run_git_command("git status", path)
        return exit_code == 0
    
    def _setup_git_config(self, path: str = None) -> bool:
        """
        Setup basic git configuration if not already set.
        """
        # Check if git config is already set
        stdout, stderr, exit_code = self._run_git_command("git config user.name", path)
        if exit_code == 0 and stdout:
            return True
        
        # Set default git config
        self._run_git_command('git config user.name "Airis AI"', path)
        self._run_git_command('git config user.email "airis@example.com"', path)
        return True
    
    def _get_git_status(self, path: str = None) -> str:
        """
        Get git status information.
        """
        stdout, stderr, exit_code = self._run_git_command("git status --porcelain", path)
        if exit_code == 0:
            return stdout
        return f"Error getting git status: {stderr}"
    
    def _add_files(self, files: list = None, path: str = None) -> tuple[str, str, int]:
        """
        Add files to git staging area.
        """
        if files:
            command = f"git add {' '.join(files)}"
        else:
            command = "git add ."
        
        return self._run_git_command(command, path)
    
    def _commit_changes(self, message: str, path: str = None) -> tuple[str, str, int]:
        """
        Commit changes with a message.
        """
        # Escape the message properly
        escaped_message = message.replace('"', '\\"')
        command = f'git commit -m "{escaped_message}"'
        return self._run_git_command(command, path)
    
    def _push_changes(self, branch: str = "main", path: str = None) -> tuple[str, str, int]:
        """
        Push changes to remote repository.
        """
        command = f"git push origin {branch}"
        return self._run_git_command(command, path)
    
    def execute(self, instruction: str, context: str | None = None, **kwargs) -> str:
        """
        Execute git operations based on the instruction.
        """
        print(f"--- GitAgent received instruction: '{instruction}' ---")
        
        # Check if we're in a git repository
        if not self._check_git_repo():
            return "エラー: 現在のディレクトリはgitリポジトリではありません。"
        
        # Parse instruction
        instruction_lower = instruction.lower()
        
        if "status" in instruction_lower or "状態" in instruction_lower:
            status = self._get_git_status()
            if status:
                return f"Git status:\n{status}"
            else:
                return "Working directory is clean."
        
        elif "add" in instruction_lower or "追加" in instruction_lower:
            # Extract specific files if mentioned
            files = []
            if "file" in instruction_lower:
                # Try to extract file names from instruction
                import re
                file_matches = re.findall(r'(\S+\.\w+)', instruction)
                files = file_matches
            
            stdout, stderr, exit_code = self._add_files(files if files else None)
            if exit_code == 0:
                return f"Files added to staging area: {stdout or 'All changes'}"
            else:
                return f"Error adding files: {stderr}"
        
        elif "commit" in instruction_lower or "コミット" in instruction_lower:
            # Extract commit message
            message = "Auto-commit by Airis"
            if "message" in instruction_lower:
                # Try to extract message from instruction
                import re
                msg_match = re.search(r'message[:\s]+["\']?([^"\']+)["\']?', instruction)
                if msg_match:
                    message = msg_match.group(1)
            
            stdout, stderr, exit_code = self._commit_changes(message)
            if exit_code == 0:
                return f"Changes committed: {stdout}"
            else:
                return f"Error committing: {stderr}"
        
        elif "push" in instruction_lower or "プッシュ" in instruction_lower:
            # Extract branch if mentioned
            branch = "main"
            if "branch" in instruction_lower:
                import re
                branch_match = re.search(r'branch[:\s]+(\w+)', instruction_lower)
                if branch_match:
                    branch = branch_match.group(1)
            
            stdout, stderr, exit_code = self._push_changes(branch)
            if exit_code == 0:
                return f"Changes pushed to {branch}: {stdout}"
            else:
                return f"Error pushing: {stderr}"
        
        elif "auto" in instruction_lower or "自動" in instruction_lower:
            # Auto workflow: setup git config, add, commit, push
            results = []
            
            # Setup git config if needed
            self._setup_git_config()
            results.append("✅ Git configuration checked/set")
            
            # Add all changes
            stdout, stderr, exit_code = self._add_files()
            if exit_code == 0:
                results.append("✅ Files added to staging area")
            else:
                results.append(f"❌ Error adding files: {stderr}")
                return "\n".join(results)
            
            # Commit with auto message
            message = "Auto-commit: Code changes by Airis"
            stdout, stderr, exit_code = self._commit_changes(message)
            if exit_code == 0:
                results.append("✅ Changes committed")
            else:
                results.append(f"❌ Error committing: {stderr}")
                return "\n".join(results)
            
            # Push to main branch
            stdout, stderr, exit_code = self._push_changes()
            if exit_code == 0:
                results.append("✅ Changes pushed to remote repository")
            else:
                results.append(f"❌ Error pushing: {stderr}")
            
            return "\n".join(results)
        
        else:
            return "利用可能なgitコマンド: status, add, commit, push, auto"
