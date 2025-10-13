import os
import re
from .base import BaseAgent
from airis.llm import LLMClient

class DocumentCompletionAgent(BaseAgent):
    """
    Agent that checks document completeness and completes incomplete documents.
    """
    
    def __init__(self):
        self.llm_client = LLMClient()
    
    def _check_document_completeness(self, content: str, doc_type: str) -> tuple[bool, str]:
        """
        Check if a document is complete based on its type and content.
        
        Returns:
            tuple: (is_complete: bool, reason: str)
        """
        # Basic checks for incomplete documents
        if not content or len(content.strip()) < 100:
            return False, "ドキュメントが短すぎます"
        
        # Check for common incomplete patterns
        incomplete_patterns = [
            r'# キャッシュ設定$',  # Ends with incomplete section
            r'return n$',  # Ends with incomplete code
            r'## セキュリティ設計$',  # Ends with section header only
            r'### 参考資料$',  # Ends with subsection header only
        ]
        
        for pattern in incomplete_patterns:
            if re.search(pattern, content.strip(), re.MULTILINE):
                return False, f"不完全なパターンを検出: {pattern}"
        
        # Check for proper ending
        if not content.strip().endswith(('.', '。', '---', '##', '#')):
            return False, "適切な終了でドキュメントが終わっていません"
        
        # Type-specific checks
        if doc_type == "requirements":
            required_sections = ["機能要件", "非機能要件", "制約事項", "受け入れ基準"]
            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
            if missing_sections:
                return False, f"必要なセクションが不足: {', '.join(missing_sections)}"
        
        elif doc_type == "design":
            required_sections = ["システム概要", "アーキテクチャ設計", "コンポーネント設計", "データ設計", "インターフェース設計", "セキュリティ設計"]
            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
            if missing_sections:
                return False, f"必要なセクションが不足: {', '.join(missing_sections)}"
        
        elif doc_type == "readme":
            required_sections = ["プロジェクト概要", "機能", "インストール方法", "使用方法"]
            missing_sections = []
            for section in required_sections:
                if section not in content:
                    missing_sections.append(section)
            if missing_sections:
                return False, f"必要なセクションが不足: {', '.join(missing_sections)}"
        
        return True, "ドキュメントは完成しています"
    
    def _complete_document(self, content: str, doc_type: str, project_name: str) -> str:
        """
        Complete an incomplete document.
        """
        completion_prompt = f"""以下の{doc_type}ドキュメントを完成させてください。

プロジェクト名: {project_name}
ドキュメントタイプ: {doc_type}

現在の内容:
{content}

以下の指示に従ってドキュメントを完成させてください：
1. 不足しているセクションを追加
2. 不完全なセクションを完成
3. 適切な終了でドキュメントを完了
4. 日本語で記述
5. Markdown形式を維持

完成したドキュメントのみを出力してください。"""
        
        response = self.llm_client.invoke(completion_prompt)
        return response.content.strip()
    
    def execute(self, instruction: str, context: str | None = None, **kwargs) -> str:
        """
        Check and complete documents based on the instruction.
        """
        
        # Extract project path from instruction or context
        project_path = None
        if "project" in instruction.lower():
            # Try to extract project name from instruction
            import re
            match = re.search(r'project[:\s]+([^\s]+)', instruction.lower())
            if match:
                project_name = match.group(1)
                project_path = f"projects/{project_name}"
        else:
            # Try to extract project name from the end of instruction
            import re
            match = re.search(r'([a-zA-Z0-9_]+)$', instruction.strip())
            if match:
                project_name = match.group(1)
                project_path = f"projects/{project_name}"
        
        if not project_path or not os.path.exists(project_path):
            return f"エラー: プロジェクトパスが見つかりません。検索したパス: {project_path}"
        
        results = []
        
        # Check and complete each document type
        doc_types = [
            ("requirements", "doc/01_requirements.md"),
            ("design", "doc/02_design.md"),
            ("readme", "README.md")
        ]
        
        for doc_type, filename in doc_types:
            file_path = os.path.join(project_path, filename)
            
            if not os.path.exists(file_path):
                results.append(f"⚠️ {filename}: ファイルが存在しません")
                continue
            
            # Read document content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check completeness
            is_complete, reason = self._check_document_completeness(content, doc_type)
            
            if is_complete:
                results.append(f"✅ {filename}: 完成済み")
            else:
                results.append(f"❌ {filename}: 未完成 - {reason}")
                
                # Complete the document
                completed_content = self._complete_document(content, doc_type, os.path.basename(project_path))
                
                # Save completed document
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(completed_content)
                
                results.append(f"🔧 {filename}: 完成させました")
        
        return "\n".join(results)
