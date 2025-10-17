"""
Interactive Mode for Airis

This module provides an interactive conversation mode where users can
have multi-turn conversations with AI to refine requirements before execution.
"""

from typing import List, Dict, Optional
from airis.config import config
from airis.system_context import get_system_context, get_capability_info
from airis.project_memory import project_memory_manager
import json


class InteractiveSession:
    """
    Manages an interactive conversation session with the user.
    
    This allows multi-turn conversations to refine requirements before
    executing the final task.
    """
    
    def __init__(self):
        # Use AI engine specified in config for interactive mode
        from airis.llm import LLMClient
        self.llm_client = LLMClient("interactive_mode")
        self.conversation_history: List[Dict[str, str]] = []
        self.requirements_gathered = False
        self.final_specification = None
    
    def start_session(self, initial_prompt: str) -> str:
        """
        Start an interactive session to gather requirements.
        
        Args:
            initial_prompt: User's initial request
            
        Returns:
            First response asking for clarification
        """
        self.conversation_history = []
        self.requirements_gathered = False
        
        # Check if user is asking about Airis itself
        prompt_lower = initial_prompt.lower()
        if any(keyword in prompt_lower for keyword in ["airisとは", "airisについて", "あなたは", "あなたの機能", "何ができる", "できること"]):
            # Return self-introduction
            return f"""{get_system_context()}

---

私Airisについて質問いただき、ありがとうございます！

{get_capability_info()}

何かお手伝いできることはありますか？
具体的なタスクをお聞かせいただければ、最適な方法で支援いたします。

例:
- 「Pythonでゲームを作って」
- 「要件定義書を生成して」
- 「このコードを分析して」
- 「Dockerの最新情報を調べて」
"""
        
        # Get system context
        system_context = get_system_context()
        
        # Get project context if available
        project_context = ""
        current_project = config.get("current_project")
        if current_project and project_memory_manager.has_memory():
            memory = project_memory_manager.get_current_memory()
            project_context = f"""
---

【現在のプロジェクト情報】
{memory.get_project_context()}

---
"""
        
        # Create clarification prompt
        clarification_prompt = f"""{system_context}
{project_context}

ユーザーから以下のリクエストを受けました：

【ユーザーのリクエスト】
{initial_prompt}

このリクエストを実行する前に、必要な要件を明確にする必要があります。
あなたの能力を活かして、最適な実装を提供するために質問してください。

重要：プロジェクト情報がある場合は、それを考慮して質問してください。
例えば、既存のファイルとの整合性、過去の仕様との互換性などを確認してください。
以下の手順で進めてください：

1. リクエストを分析し、不明確な点や追加で確認すべき点をリストアップ
2. ユーザーに質問を投げかけ、要件を詰める
3. 質問は具体的で、選択肢があればそれを提示する
4. 一度に3-5個の質問に絞る

以下の形式で応答してください：

【分析】
(リクエストの簡潔な分析)

【確認事項】
1. (質問1)
   選択肢: A) ... B) ... C) ...
2. (質問2)
   選択肢: ...
...

【次のステップ】
これらの確認事項が明確になれば、実装を開始できます。
"""
        
        response = self.llm_client.invoke(clarification_prompt)
        response_text = response.content.strip()
        
        # Store in conversation history
        self.conversation_history.append({
            "role": "user",
            "content": initial_prompt
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": response_text
        })
        
        return response_text
    
    def continue_conversation(self, user_response: str) -> tuple[bool, str]:
        """
        Continue the conversation with user's response.
        
        Args:
            user_response: User's answer to the clarification questions
            
        Returns:
            Tuple of (is_complete, response_or_specification)
            - is_complete: True if requirements are fully gathered
            - response_or_specification: Next question or final specification
        """
        # Add user response to history
        self.conversation_history.append({
            "role": "user",
            "content": user_response
        })
        
        # Get system context
        system_context = get_system_context()
        
        # Build conversation context
        conversation_context = self._build_conversation_context()
        
        # Create continuation prompt
        continuation_prompt = f"""{system_context}

---

これまでの会話：

{conversation_context}

【ユーザーの最新の回答】
{user_response}

これまでの会話を踏まえて、あなた（Airis）の能力を考慮し、以下のいずれかを実行してください：

A) まだ不明確な点がある場合：
   追加の質問を投げかけてください。形式：
   
   【追加確認事項】
   1. (質問)
      選択肢: ...
   2. (質問)
   ...

B) 要件が十分に明確になった場合：
   最終的な仕様をまとめてください。形式：
   
   【要件確定】
   
   【最終仕様】
   - 機能: ...
   - 入力方法: ...
   - 出力形式: ...
   - エラーハンドリング: ...
   - その他: ...
   
   【実装準備完了】
   この仕様で実装を開始できます。

どちらかの形式で応答してください。
"""
        
        response = self.llm_client.invoke(continuation_prompt)
        response_text = response.content.strip()
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": response_text
        })
        
        # Check if requirements are complete
        if "【要件確定】" in response_text or "【実装準備完了】" in response_text:
            self.requirements_gathered = True
            self.final_specification = self._extract_specification(response_text)
            return True, response_text
        else:
            return False, response_text
    
    def _build_conversation_context(self) -> str:
        """Build a formatted conversation context."""
        context_parts = []
        for i, msg in enumerate(self.conversation_history):
            role = "ユーザー" if msg["role"] == "user" else "Airis"
            context_parts.append(f"【{role}】\n{msg['content']}\n")
        return "\n".join(context_parts)
    
    def _extract_specification(self, response: str) -> Dict[str, str]:
        """
        Extract structured specification from the final response.
        
        Args:
            response: Final response containing specification
            
        Returns:
            Dictionary containing extracted specification
        """
        spec = {
            "full_text": response,
            "requirements": [],
            "constraints": [],
            "implementation_notes": []
        }
        
        # Simple extraction (can be enhanced with more sophisticated parsing)
        lines = response.split("\n")
        current_section = None
        
        for line in lines:
            line = line.strip()
            if "機能:" in line or "- 機能:" in line:
                spec["requirements"].append(line.replace("- ", "").replace("機能:", "").strip())
            elif "入力" in line and ":" in line:
                spec["requirements"].append(line)
            elif "出力" in line and ":" in line:
                spec["requirements"].append(line)
            elif "エラー" in line and ":" in line:
                spec["constraints"].append(line)
        
        return spec
    
    def get_final_prompt(self) -> str:
        """
        Generate the final prompt for task execution based on gathered requirements.
        
        Returns:
            Optimized prompt for task execution
        """
        if not self.requirements_gathered:
            return None
        
        # Build comprehensive prompt from specification
        if self.final_specification:
            prompt_parts = ["以下の仕様に基づいて実装してください：\n"]
            prompt_parts.append(self.final_specification["full_text"])
            return "\n".join(prompt_parts)
        
        return None
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation."""
        if not self.conversation_history:
            return "No conversation history"
        
        summary = f"会話ターン数: {len(self.conversation_history)}\n"
        summary += f"要件確定: {'はい' if self.requirements_gathered else 'いいえ'}\n"
        return summary


class InteractiveOrchestrator:
    """
    Orchestrator for interactive mode.
    
    Manages the flow of interactive conversations and task execution.
    """
    
    def __init__(self, orchestrator):
        """
        Initialize interactive orchestrator.
        
        Args:
            orchestrator: Main Orchestrator instance for task execution
        """
        self.orchestrator = orchestrator
        self.current_session: Optional[InteractiveSession] = None
    
    def start_interactive_mode(self, initial_prompt: str) -> str:
        """
        Start interactive mode with initial prompt.
        
        Args:
            initial_prompt: User's initial request
            
        Returns:
            First clarification questions
        """
        self.current_session = InteractiveSession()
        return self.current_session.start_session(initial_prompt)
    
    def process_user_input(self, user_input: str) -> tuple[bool, str, Optional[str]]:
        """
        Process user input in interactive mode.
        
        Args:
            user_input: User's response
            
        Returns:
            Tuple of (is_complete, response, execution_result)
            - is_complete: Whether requirements gathering is complete
            - response: Next question or confirmation message
            - execution_result: Task execution result if complete, None otherwise
        """
        if not self.current_session:
            return False, "Error: No active session. Use 'start' command first.", None
        
        # Check for special commands
        if user_input.lower() in ["cancel", "キャンセル", "quit", "exit"]:
            self.current_session = None
            return True, "対話モードを終了しました。", None
        
        if user_input.lower() in ["execute", "実行", "run", "ok", "proceed"]:
            # User wants to proceed with current understanding
            if self.current_session.requirements_gathered:
                final_prompt = self.current_session.get_final_prompt()
                result, code = self.orchestrator.delegate_task(final_prompt)
                
                # Save to project memory
                from airis.config import config
                current_project = config.get("current_project")
                if current_project and project_memory_manager.has_memory():
                    memory = project_memory_manager.get_current_memory()
                    memory.add_conversation(
                        user_prompt=final_prompt,
                        ai_response=result,
                        task_type="interactive_session"
                    )
                    if self.current_session.final_specification:
                        for req in self.current_session.final_specification.get("requirements", []):
                            memory.add_note(f"要件: {req}")
                
                self.current_session = None
                return True, "要件に基づいて実行しました。", result
            else:
                return False, "まだ要件が十分に明確になっていません。もう少し詳細を教えてください。", None
        
        # Continue conversation
        is_complete, response = self.current_session.continue_conversation(user_input)
        
        if is_complete:
            # Requirements are gathered, ask for confirmation
            confirmation_msg = f"{response}\n\n以下のコマンドを選択してください：\n"
            confirmation_msg += "- 'execute' または '実行': この仕様で実装を開始\n"
            confirmation_msg += "- 'modify' または '修正': 仕様を修正\n"
            confirmation_msg += "- 'cancel' または 'キャンセル': 中止"
            return False, confirmation_msg, None
        else:
            return False, response, None
    
    def has_active_session(self) -> bool:
        """Check if there's an active interactive session."""
        return self.current_session is not None
    
    def get_session_info(self) -> str:
        """Get current session information."""
        if not self.current_session:
            return "対話モードは開始されていません。"
        
        return self.current_session.get_conversation_summary()

