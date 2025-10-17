from agents.code_agent import CodeAgent
from agents.shell_agent import ShellAgent
from agents.cursor_agent import CursorAgent
from agents.web_search_agent import WebSearchAgent
from agents.web_browser_agent import WebBrowserAgent
from agents.document_completion_agent import DocumentCompletionAgent
from agents.git_agent import GitAgent
from agents.gemini_agent import GeminiAgent
from agents.validator_agent import ValidatorAgent
from airis.llm import llm_client
from airis.config import config
from airis.ai_engine_manager import ai_engine_manager
from airis.ai_engine_commands import ai_engine_commands
from airis.system_context import get_system_context, get_capability_info
import os
import difflib

class Orchestrator:
    def __init__(self):
        self.agents = {
            "code": CodeAgent(),
            "shell": ShellAgent(),
            "cursor": CursorAgent(),
            "web_search": WebSearchAgent(),
            "web_browser": WebBrowserAgent(),
            "doc_completion": DocumentCompletionAgent(),
            "git": GitAgent(),
            "gemini": GeminiAgent(),
            "validator": ValidatorAgent(),
        }
        # Validation settings
        self.enable_validation = config.get("enable_output_validation", True)
        self.validation_tasks = config.get("validation_tasks", [
            "code_generation", 
            "document_generation", 
            "code_analysis"
        ])

    def delegate_task(self, user_prompt: str) -> tuple[str, str | None]:
        """
        Delegates the user's task to the appropriate agent based on keywords.
        Returns a tuple of (display_result_string, generated_code_string).
        If no code is generated (e.g., for shell agent), generated_code_string will be None.
        """
        # Check if user is asking about Airis itself
        prompt_lower = user_prompt.lower()
        if any(keyword in prompt_lower for keyword in ["airisとは", "airisについて", "airisの機能", "あなたは誰", "何ができる", "できること"]):
            system_context = get_system_context()
            capability_info = get_capability_info()
            return f"""{system_context}

---

{capability_info}

何かお手伝いできることはありますか？
具体的なタスクをお聞かせいただければ、最適な方法で支援いたします。
""", None
        
        # Check for document generation intent
        # Check for a full development cycle request
        if user_prompt.lower().startswith("develop:"):
            return self._handle_development_cycle(user_prompt.replace("develop:", "").strip())

        # NEW: Check for Cursor editing intent
        if user_prompt.lower().startswith("edit in cursor:"):
            return self._handle_cursor_edit(user_prompt.replace("edit in cursor:", "").strip())

        # Check for document generation intent
        if user_prompt.lower().startswith("generate docs"):
            current_project = config.get("current_project")
            if not current_project:
                return "Error: No active project selected. Please use 'use project [project_name]' first.", None
            
            projects_root = config.get("projects_root_dir", "projects")
            project_doc_path = os.path.join(projects_root, current_project, "doc")
            os.makedirs(project_doc_path, exist_ok=True)

            doc_type = user_prompt.lower().replace("generate docs", "").strip()
            if "requirements" in doc_type:
                filename = "01_requirements.md"
                doc_prompt = f"""プロジェクト「{current_project}」の詳細な要件定義書を日本語で生成してください。機能要件と非機能要件に焦点を当ててください。Markdown形式で出力してください。

以下の構成で記述してください：
1. プロジェクト概要
2. 機能要件
3. 非機能要件
4. 制約事項
5. 受け入れ基準

重要：ドキュメントを完全に生成してください。途中で切れずに、すべてのセクションを最後まで記述してください。
日本語で記述し、技術的な内容も分かりやすく説明してください。"""
            elif "design" in doc_type:
                filename = "02_design.md"
                doc_prompt = f"""プロジェクト「{current_project}」の詳細なシステム設計書を日本語で生成してください。アーキテクチャとコンポーネント設計に焦点を当ててください。Markdown形式で出力してください。

以下の構成で記述してください：
1. システム概要
2. アーキテクチャ設計
3. コンポーネント設計
4. データ設計
5. インターフェース設計
6. セキュリティ設計

重要：ドキュメントを完全に生成してください。途中で切れずに、すべてのセクションを最後まで記述してください。
日本語で記述し、技術的な内容も分かりやすく説明してください。"""
            elif "readme" in doc_type:
                filename = "README.md"
                doc_prompt = f"""プロジェクト「{current_project}」のREADME.mdを日本語で生成してください。Markdown形式で出力してください。

以下の構成で記述してください：
1. プロジェクト概要
2. 機能
3. インストール方法
4. 使用方法
5. ファイル構成
6. ライセンス
7. 貢献方法

日本語で記述し、プロジェクトの使い方を分かりやすく説明してください。"""
            else:
                filename = "README.md"
                doc_prompt = f"""プロジェクト「{current_project}」のREADME.mdを日本語で生成してください。Markdown形式で出力してください。

以下の構成で記述してください：
1. プロジェクト概要
2. 機能
3. インストール方法
4. 使用方法
5. ファイル構成
6. ライセンス
7. 貢献方法

日本語で記述し、プロジェクトの使い方を分かりやすく説明してください。"""
            
            doc_content_response = llm_client.invoke(doc_prompt)
            doc_content = doc_content_response.content.strip()

            file_path = os.path.join(project_doc_path, filename)
            with open(file_path, "w") as f:
                f.write(doc_content)
            
            return f"Document '{filename}' generated and saved to '{file_path}'.", None

        # Check for AI engine management commands
        if user_prompt.lower().startswith("ai engine"):
            result = self._handle_ai_engine_command(user_prompt)
            return result, None
        
        # Use AI Engine Manager for intelligent routing
        task_type = self._determine_task_type(user_prompt)
        selected_engine = ai_engine_manager.get_engine_for_task(task_type, user_prompt)
        agent_name = self._map_engine_to_agent(selected_engine, user_prompt)
        

        agent = self.agents[agent_name]
        
        if agent_name == "code":
            execution_result, generated_code = agent.execute(user_prompt)
            
            # Ask LLM to suggest a filename
            filename_prompt = f"""Based on the following user prompt and generated Python code, suggest a single, appropriate filename (e.g., main.py, fibonacci.py). Do not include any explanation or markdown formatting.

User Prompt: {user_prompt}
Generated Code:\n{generated_code}
Filename:"""
            suggested_filename_response = llm_client.invoke(filename_prompt)
            suggested_filename = suggested_filename_response.content.strip()

            # Save code to file if user approves
            current_project = config.get("current_project")
            if current_project:
                projects_root = config.get("projects_root_dir", "projects")
                project_src_path = os.path.join(projects_root, current_project, "src")
                os.makedirs(project_src_path, exist_ok=True)
                
                code_file_path = os.path.join(project_src_path, suggested_filename)
                with open(code_file_path, "w") as f:
                    f.write(generated_code)
                
                # Auto git commit after code generation
                git_agent = self.agents["git"]
                if git_agent._check_git_repo():
                    git_result = git_agent.execute("git auto")
                    display_result = f"{execution_result}\nCode saved to: {code_file_path}\nGit update: {git_result}"
                else:
                    display_result = f"{execution_result}\nCode saved to: {code_file_path}"
            else:
                display_result = f"{execution_result}\nSuggested filename: {suggested_filename}"
            
            # Validate code if enabled
            if self.enable_validation and task_type in self.validation_tasks:
                is_valid, validated_output, validation_msg = self._validate_output(
                    task_type, user_prompt, execution_result
                )
                display_result = f"{display_result}\n\n{validation_msg}"
            
            return display_result, generated_code
        elif agent_name in ["web_search", "web_browser", "doc_completion", "git", "gemini", "cursor"]:
            # Execute agent
            result = agent.execute(user_prompt)
            
            # Validate output if enabled
            if self.enable_validation and task_type in self.validation_tasks:
                is_valid, validated_result, validation_msg = self._validate_output(
                    task_type, user_prompt, result
                )
                result = f"{result}\n\n--- VALIDATION ---\n{validation_msg}"
            
            return result, None
        else:
            # For shell agent, no code is generated for saving
            result = agent.execute(user_prompt)
            return result, None

    def _handle_development_cycle(self, task_description: str) -> tuple[str, str | None]:
        current_project = config.get("current_project")
        if not current_project:
            return "Error: No active project selected. Please use 'use project [project_name]' first.", None

        projects_root = config.get("projects_root_dir", "projects")
        project_doc_path = os.path.join(projects_root, current_project, "doc")
        project_src_path = os.path.join(projects_root, current_project, "src")
        os.makedirs(project_doc_path, exist_ok=True)
        os.makedirs(project_src_path, exist_ok=True)

        # 1. Generate Requirements Document
        req_filename = "01_requirements.md"
        req_prompt = f"""プロジェクト「{task_description}」の要件定義書を日本語で生成してください。Markdown形式で出力してください。

以下の構成で記述してください：
1. プロジェクト概要
2. 機能要件
3. 非機能要件
4. 制約事項
5. 受け入れ基準

各セクションは簡潔に、しかし完全に記述してください。
日本語で記述し、技術的な内容も分かりやすく説明してください。"""
        req_content_response = llm_client.invoke(req_prompt)
        req_content = req_content_response.content.strip()
        req_file_path = os.path.join(project_doc_path, req_filename)
        with open(req_file_path, "w") as f:
            f.write(req_content)
        display_result = f"Document '{req_filename}' generated and saved to '{req_file_path}'.\n"

        # 2. Generate Design Document
        design_filename = "02_design.md"
        design_prompt = f"""プロジェクト「{task_description}」のシステム設計書を日本語で生成してください。

以下の要件を考慮してください：
{req_content}

以下の構成で記述してください：
1. システム概要
2. アーキテクチャ設計
3. コンポーネント設計
4. データ設計
5. インターフェース設計
6. セキュリティ設計

各セクションは簡潔に、しかし完全に記述してください。
日本語で記述し、技術的な内容も分かりやすく説明してください。

重要：ドキュメントを完全に生成してください。各セクションを最後まで記述し、適切な終了でドキュメントを完了してください。"""
        design_content_response = llm_client.invoke(design_prompt)
        design_content = design_content_response.content.strip()
        
        # Check if document seems incomplete and try to complete it
        if not design_content.endswith(('.', '。', '---', '##', '#')) or len(design_content.split('\n')) < 50:
            completion_prompt = f"""以下の設計書の続きを生成してください。ドキュメントを完全に終了させてください。

現在の内容：
{design_content}

続きを生成し、適切な終了でドキュメントを完了してください。"""
            completion_response = llm_client.invoke(completion_prompt)
            design_content += "\n\n" + completion_response.content.strip()
        
        design_file_path = os.path.join(project_doc_path, design_filename)
        with open(design_file_path, "w") as f:
            f.write(design_content)
        display_result += f"Document '{design_filename}' generated and saved to '{design_file_path}'.\n"

        # 3. Generate Code
        code_agent = self.agents["code"]
        code_prompt = f"""Based on the following requirements and design, generate Python code to {task_description}.
Requirements:
{req_content}

Design:
{design_content}

Output only the Python code.
"""
        execution_result, generated_code = code_agent.execute(code_prompt)

        # Ask LLM to suggest a filename for the code
        filename_prompt = f"""Based on the following user prompt and generated Python code, suggest a single, appropriate filename (e.g., main.py, fibonacci.py). Do not include any explanation or markdown formatting.

User Prompt: {task_description}
Generated Code:\n{generated_code}
Filename:"""
        suggested_filename_response = llm_client.invoke(filename_prompt)
        suggested_filename = suggested_filename_response.content.strip()

        code_file_path = os.path.join(project_src_path, suggested_filename)
        with open(code_file_path, "w") as f:
            f.write(generated_code)
        display_result += f"Code generated and saved to '{code_file_path}'.\n"
        display_result += execution_result # Include execution result from code agent
        
        # Auto git commit after code generation
        git_agent = self.agents["git"]
        if git_agent._check_git_repo():
            git_result = git_agent.execute("git auto")
            display_result += f"\nGit update: {git_result}\n"

        # 4. Generate README.md
        readme_filename = "README.md"
        readme_prompt = f"""プロジェクト「{task_description}」のREADME.mdを日本語で生成してください。Markdown形式で出力してください。

以下の要件と設計を考慮してください：
要件：
{req_content}

設計：
{design_content}

生成されたコード：
{generated_code}

以下の構成で記述してください：
1. プロジェクト概要
2. 機能
3. インストール方法
4. 使用方法
5. ファイル構成
6. ライセンス
7. 貢献方法

各セクションは簡潔に、しかし完全に記述してください。
日本語で記述し、プロジェクトの使い方を分かりやすく説明してください。

重要：ドキュメントを完全に生成してください。各セクションを最後まで記述し、適切な終了でドキュメントを完了してください。"""
        readme_content_response = llm_client.invoke(readme_prompt)
        readme_content = readme_content_response.content.strip()
        
        # Check if README seems incomplete and try to complete it
        if not readme_content.endswith(('.', '。', '---', '##', '#')) or len(readme_content.split('\n')) < 30:
            completion_prompt = f"""以下のREADMEの続きを生成してください。ドキュメントを完全に終了させてください。

現在の内容：
{readme_content}

続きを生成し、適切な終了でドキュメントを完了してください。"""
            completion_response = llm_client.invoke(completion_prompt)
            readme_content += "\n\n" + completion_response.content.strip()
        
        readme_file_path = os.path.join(projects_root, current_project, readme_filename)
        with open(readme_file_path, "w") as f:
            f.write(readme_content)
        display_result += f"README.md generated and saved to '{readme_file_path}'.\n"

        return display_result, generated_code

    # NEW: _handle_cursor_edit method
    def _handle_cursor_edit(self, task_description: str) -> tuple[str, str | None]:
        cursor_agent = self.agents["cursor"]
        code_agent = self.agents["code"]

        # 1. Get active file content from Cursor
        file_path, original_content = cursor_agent.get_active_file_content()
        if not file_path:
            return "Error: Could not get active file content from Cursor. Is a file open and Cursor Background Agent running?", None
        if not original_content:
            return f"Error: Active file '{file_path}' is empty or could not be read.", None

        # 2. Generate new code based on task and original content
        code_prompt = f"""Based on the following file content and task, generate the corrected or new Python code.
Only output the code, without any explanation or markdown formatting.

File Path: {file_path}
File Content:
{original_content}

Task: {task_description}
"""
        execution_result, generated_code = code_agent.execute(code_prompt)

        if "Code executed successfully." not in execution_result:
            return f"Code generation or execution failed: {execution_result}", generated_code

        # 3. Generate a diff and apply it to Cursor
        # difflib.unified_diff returns a generator, convert to list and join
        diff_lines = difflib.unified_diff(
            original_content.splitlines(keepends=True),
            generated_code.splitlines(keepends=True),
            fromfile=file_path,
            tofile=file_path,
            lineterm='' # Important for consistent diff across OS
        )
        diff_content = "".join(list(diff_lines))

        if not diff_content:
            return f"No changes detected for '{file_path}'. Code is already up to date.", None

        apply_success = cursor_agent.apply_diff(file_path, diff_content)

        if apply_success:
            return f"Changes applied to '{file_path}' in Cursor successfully.", generated_code
        else:
            return f"Error: Failed to apply changes to '{file_path}' in Cursor.", generated_code
    
    def _determine_task_type(self, user_prompt: str) -> str:
        """Determine the type of task based on user prompt."""
        prompt_lower = user_prompt.lower()
        
        if any(keyword in prompt_lower for keyword in ["search", "find", "look up", "web search"]):
            return "web_search"
        elif any(keyword in prompt_lower for keyword in ["browse", "visit", "url", "http", "https", "website"]):
            return "web_browsing"
        elif any(keyword in prompt_lower for keyword in ["complete", "finish", "complete doc", "ドキュメント完成", "完成"]):
            return "document_completion"
        elif any(keyword in prompt_lower for keyword in ["git", "commit", "push", "add", "status", "git管理", "コミット", "プッシュ"]):
            return "git_operations"
        elif any(keyword in prompt_lower for keyword in ["analyze", "document", "improve", "分析", "ドキュメント", "改善"]):
            return "code_analysis"
        elif any(keyword in prompt_lower for keyword in ["code", "python", "program", "script", "write", "create", "generate", "function", "class"]):
            return "code_generation"
        elif any(keyword in prompt_lower for keyword in ["shell", "command", "execute", "run"]):
            return "shell_operations"
        else:
            return "code_generation"  # Default task type
    
    def _validate_output(self, task_type: str, original_prompt: str, output: str) -> tuple[bool, str, str]:
        """
        Validate the output using ValidatorAgent.
        
        Args:
            task_type: Type of task
            original_prompt: Original user prompt
            output: Output to validate
            
        Returns:
            Tuple of (is_valid, validated_output, validation_message)
        """
        if not self.enable_validation:
            return True, output, "Validation disabled"
        
        if task_type not in self.validation_tasks:
            return True, output, "Validation not required for this task type"
        
        # Skip validation for very short outputs
        if len(output) < 50:
            return True, output, "Output too short to validate"
        
        validator = self.agents["validator"]
        instruction = f"validate: {task_type} | {original_prompt} | {output}"
        
        try:
            validation_result = validator.execute(instruction)
            
            if validation_result.startswith("VALIDATION_OK"):
                return True, output, "✓ 検証完了: 品質基準を満たしています"
            
            elif validation_result.startswith("VALIDATION_NG"):
                parts = validation_result.split("|", 1)
                message = parts[1] if len(parts) > 1 else "重大な問題が検出されました"
                return False, output, f"✗ 検証失敗:\n{message}"
            
            elif validation_result.startswith("VALIDATION_NEEDS_IMPROVEMENT"):
                parts = validation_result.split("|", 1)
                message = parts[1] if len(parts) > 1 else "改善の余地があります"
                return True, output, f"⚠ 改善推奨:\n{message}"
            
            else:
                return True, output, "⚠ 検証でエラーが発生しましたが、出力は返却されます"
                
        except Exception as e:
            return True, output, f"⚠ 検証エラー: {str(e)}"
    
    def _map_engine_to_agent(self, engine: str, user_prompt: str) -> str:
        """Map AI engine to agent name."""
        engine_to_agent = {
            "claude": "code",  # Claude uses code agent
            "gemini": "gemini",
            "cursor": "cursor",
            "web_search": "web_search",
            "web_browser": "web_browser",
            "local": "code"  # Local operations use code agent
        }
        
        # Special handling for specific keywords
        prompt_lower = user_prompt.lower()
        
        if "gemini" in prompt_lower:
            return "gemini"
        elif "cursor" in prompt_lower:
            return "cursor"
        elif "search" in prompt_lower or "find" in prompt_lower:
            return "web_search"
        elif "browse" in prompt_lower or "url" in prompt_lower:
            return "web_browser"
        elif "git" in prompt_lower:
            return "git"
        elif "shell" in prompt_lower or "command" in prompt_lower:
            return "shell"
        
        return engine_to_agent.get(engine, "code")
    
    def _handle_ai_engine_command(self, user_prompt: str) -> str:
        """Handle AI engine management commands."""
        prompt_lower = user_prompt.lower()
        
        if "set default" in prompt_lower:
            # Extract engine name after "set default"
            parts = user_prompt.split()
            try:
                default_index = parts.index("default")
                if default_index + 1 < len(parts):
                    engine = parts[default_index + 1]
                    return ai_engine_commands.set_default_engine(engine)
                else:
                    return "Usage: ai engine set default <engine_name>"
            except ValueError:
                return "Usage: ai engine set default <engine_name>"
        
        elif "set task" in prompt_lower:
            # Extract task type and engine
            parts = user_prompt.split()
            if len(parts) >= 5:
                task_type = parts[3]
                engine = parts[4]
                return ai_engine_commands.set_task_routing(task_type, engine)
            else:
                return "Usage: ai engine set task <task_type> <engine_name>"
        
        elif "enable compliance" in prompt_lower:
            # Extract allowed engines after "enable compliance"
            parts = user_prompt.split()
            try:
                compliance_index = parts.index("compliance")
                if compliance_index + 1 < len(parts):
                    allowed_engines = parts[compliance_index + 1:]
                    return ai_engine_commands.enable_compliance_mode(allowed_engines)
                else:
                    return ai_engine_commands.enable_compliance_mode()
            except ValueError:
                return ai_engine_commands.enable_compliance_mode()
        
        elif "disable compliance" in prompt_lower:
            return ai_engine_commands.disable_compliance_mode()
        
        elif "enable cost optimization" in prompt_lower:
            return ai_engine_commands.enable_cost_optimization()
        
        elif "disable cost optimization" in prompt_lower:
            return ai_engine_commands.disable_cost_optimization()
        
        elif "set availability" in prompt_lower:
            # Extract engine and availability
            parts = user_prompt.split()
            if len(parts) >= 5:
                engine = parts[3]
                available = parts[4].lower() in ["true", "1", "yes", "on"]
                return ai_engine_commands.set_engine_availability(engine, available)
            else:
                return "Usage: ai engine set availability <engine_name> <true/false>"
        
        elif "info" in prompt_lower or "status" in prompt_lower:
            return ai_engine_commands.get_engine_info()
        
        elif "debug" in prompt_lower:
            return ai_engine_commands.debug_config()
        
        elif "save" in prompt_lower:
            return ai_engine_commands.save_config()
        
        elif "reset" in prompt_lower:
            return ai_engine_commands.reset_to_defaults()
        
        else:
            return """AI Engine Commands:
- ai engine set default <engine_name>
- ai engine set task <task_type> <engine_name>
- ai engine enable compliance [allowed_engines...]
- ai engine disable compliance
- ai engine enable cost optimization
- ai engine disable cost optimization
- ai engine set availability <engine_name> <true/false>
- ai engine info
- ai engine debug
- ai engine save
- ai engine reset"""