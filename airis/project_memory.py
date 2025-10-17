"""
Project Memory System

This module manages project-specific memory and context to enable
continuation of work on existing projects.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class ProjectMemory:
    """
    Manages memory and context for each project.
    
    Stores:
    - Project metadata
    - Conversation history
    - Generated files
    - Requirements and specifications
    - Previous AI interactions
    """
    
    def __init__(self, project_name: str, projects_root: str = "projects"):
        self.project_name = project_name
        self.projects_root = projects_root
        self.project_path = os.path.join(projects_root, project_name)
        self.memory_path = os.path.join(self.project_path, ".airis_memory")
        self.memory_file = os.path.join(self.memory_path, "context.json")
        
        # Initialize memory directory
        os.makedirs(self.memory_path, exist_ok=True)
        
        # Load or initialize memory
        self.memory = self._load_memory()
    
    def _load_memory(self) -> Dict:
        """Load project memory from file."""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load project memory: {e}")
                return self._create_empty_memory()
        else:
            return self._create_empty_memory()
    
    def _create_empty_memory(self) -> Dict:
        """Create empty memory structure."""
        return {
            "project_name": self.project_name,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "description": "",
            "requirements": [],
            "specifications": {},
            "conversation_history": [],
            "generated_files": [],
            "ai_interactions": [],
            "technologies": [],
            "notes": []
        }
    
    def save_memory(self):
        """Save memory to file."""
        self.memory["last_updated"] = datetime.now().isoformat()
        
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save project memory: {e}")
    
    def add_conversation(self, user_prompt: str, ai_response: str, task_type: str = "general"):
        """Add a conversation to memory."""
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "user_prompt": user_prompt,
            "ai_response": ai_response[:500] + "..." if len(ai_response) > 500 else ai_response
        }
        
        self.memory["conversation_history"].append(conversation)
        
        # Keep only last 50 conversations
        if len(self.memory["conversation_history"]) > 50:
            self.memory["conversation_history"] = self.memory["conversation_history"][-50:]
        
        self.save_memory()
    
    def add_generated_file(self, file_path: str, file_type: str, description: str = ""):
        """Record a generated file."""
        file_info = {
            "timestamp": datetime.now().isoformat(),
            "path": file_path,
            "type": file_type,
            "description": description
        }
        
        self.memory["generated_files"].append(file_info)
        self.save_memory()
    
    def update_requirements(self, requirements: List[str]):
        """Update project requirements."""
        self.memory["requirements"] = requirements
        self.save_memory()
    
    def update_specifications(self, spec_key: str, spec_value: any):
        """Update project specifications."""
        self.memory["specifications"][spec_key] = spec_value
        self.save_memory()
    
    def add_ai_interaction(self, agent_name: str, task: str, result: str):
        """Record an AI interaction."""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "task": task,
            "result": result[:200] + "..." if len(result) > 200 else result
        }
        
        self.memory["ai_interactions"].append(interaction)
        
        # Keep only last 30 interactions
        if len(self.memory["ai_interactions"]) > 30:
            self.memory["ai_interactions"] = self.memory["ai_interactions"][-30:]
        
        self.save_memory()
    
    def add_note(self, note: str):
        """Add a note to project memory."""
        note_entry = {
            "timestamp": datetime.now().isoformat(),
            "content": note
        }
        
        self.memory["notes"].append(note_entry)
        self.save_memory()
    
    def get_project_context(self) -> str:
        """
        Get formatted project context for LLM prompts.
        
        Returns:
            Formatted context string
        """
        context_parts = []
        
        context_parts.append(f"# プロジェクト: {self.project_name}")
        context_parts.append(f"作成日: {self.memory.get('created_at', 'Unknown')}")
        context_parts.append(f"最終更新: {self.memory.get('last_updated', 'Unknown')}")
        
        if self.memory.get("description"):
            context_parts.append(f"\n## プロジェクト概要")
            context_parts.append(self.memory["description"])
        
        if self.memory.get("requirements"):
            context_parts.append(f"\n## 要件")
            for req in self.memory["requirements"]:
                context_parts.append(f"- {req}")
        
        if self.memory.get("specifications"):
            context_parts.append(f"\n## 仕様")
            for key, value in self.memory["specifications"].items():
                context_parts.append(f"- {key}: {value}")
        
        if self.memory.get("technologies"):
            context_parts.append(f"\n## 使用技術")
            context_parts.append(", ".join(self.memory["technologies"]))
        
        if self.memory.get("generated_files"):
            context_parts.append(f"\n## 生成済みファイル")
            recent_files = self.memory["generated_files"][-10:]  # Last 10 files
            for file_info in recent_files:
                context_parts.append(f"- {file_info['path']} ({file_info['type']})")
        
        if self.memory.get("conversation_history"):
            context_parts.append(f"\n## 最近の会話")
            recent_convs = self.memory["conversation_history"][-5:]  # Last 5 conversations
            for conv in recent_convs:
                context_parts.append(f"- [{conv['task_type']}] {conv['user_prompt'][:80]}")
        
        if self.memory.get("notes"):
            context_parts.append(f"\n## メモ")
            for note in self.memory["notes"][-5:]:  # Last 5 notes
                context_parts.append(f"- {note['content'][:100]}")
        
        return "\n".join(context_parts)
    
    def get_summary(self) -> str:
        """Get a brief summary of the project."""
        summary = f"プロジェクト: {self.project_name}\n"
        summary += f"会話履歴: {len(self.memory.get('conversation_history', []))}件\n"
        summary += f"生成ファイル: {len(self.memory.get('generated_files', []))}件\n"
        summary += f"最終更新: {self.memory.get('last_updated', 'Unknown')}\n"
        
        if self.memory.get("description"):
            summary += f"概要: {self.memory['description'][:100]}\n"
        
        return summary
    
    def analyze_project_files(self):
        """Analyze project files and update memory."""
        # Scan src directory
        src_path = os.path.join(self.project_path, "src")
        if os.path.exists(src_path):
            files = []
            for file in os.listdir(src_path):
                if file.endswith('.py'):
                    file_path = os.path.join(src_path, file)
                    # Read file to get basic info
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Extract docstring if exists
                            if '"""' in content:
                                files.append({
                                    "name": file,
                                    "type": "python",
                                    "lines": len(content.split('\n'))
                                })
                    except Exception:
                        pass
            
            if files and "analyzed_files" not in self.memory:
                self.memory["analyzed_files"] = files
                self.save_memory()
    
    def get_recent_context(self, num_items: int = 5) -> str:
        """Get recent context for continuation."""
        context = []
        
        # Recent conversations
        if self.memory.get("conversation_history"):
            context.append("## 最近の会話:")
            for conv in self.memory["conversation_history"][-num_items:]:
                context.append(f"- {conv['user_prompt'][:100]}")
        
        # Recent files
        if self.memory.get("generated_files"):
            context.append("\n## 最近生成したファイル:")
            for file_info in self.memory["generated_files"][-num_items:]:
                context.append(f"- {file_info['path']}")
        
        return "\n".join(context) if context else "このプロジェクトには履歴がありません"


class ProjectMemoryManager:
    """
    Global manager for project memories.
    """
    
    def __init__(self):
        self.current_memory: Optional[ProjectMemory] = None
    
    def load_project_memory(self, project_name: str, projects_root: str = "projects") -> ProjectMemory:
        """Load memory for a specific project."""
        self.current_memory = ProjectMemory(project_name, projects_root)
        return self.current_memory
    
    def get_current_memory(self) -> Optional[ProjectMemory]:
        """Get current project memory."""
        return self.current_memory
    
    def has_memory(self) -> bool:
        """Check if current project has memory loaded."""
        return self.current_memory is not None


# Global instance
project_memory_manager = ProjectMemoryManager()

