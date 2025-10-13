import os
import google.generativeai as genai
from .base import BaseAgent
from airis.config import config

class GeminiAgent(BaseAgent):
    """
    Agent that uses Google's Gemini API for various tasks.
    """
    
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found in environment variables.")
            return
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        # Use the latest stable model with correct API version
        self.model = genai.GenerativeModel('gemini-2.5-pro', generation_config=genai.types.GenerationConfig(
            max_output_tokens=4000,
            temperature=0.1,
        ))
        
        # Configuration
        self.max_tokens = config.get("gemini_max_tokens", 4000)
        self.temperature = config.get("gemini_temperature", 0.1)
    
    def _generate_content(self, prompt: str) -> str:
        """
        Generate content using Gemini API.
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.max_tokens,
                    temperature=self.temperature,
                )
            )
            return response.text
        except Exception as e:
            return f"エラー: Gemini API呼び出しに失敗しました - {e}"
    
    def _analyze_code(self, code: str, analysis_type: str = "general") -> str:
        """
        Analyze code using Gemini.
        """
        if analysis_type == "security":
            prompt = f"""以下のPythonコードをセキュリティの観点から分析してください。
潜在的な脆弱性、セキュリティリスク、改善提案を含めてください。

コード:
```python
{code}
```

分析結果を日本語で提供してください。"""
        
        elif analysis_type == "performance":
            prompt = f"""以下のPythonコードをパフォーマンスの観点から分析してください。
ボトルネック、最適化の機会、改善提案を含めてください。

コード:
```python
{code}
```

分析結果を日本語で提供してください。"""
        
        elif analysis_type == "quality":
            prompt = f"""以下のPythonコードをコード品質の観点から分析してください。
可読性、保守性、ベストプラクティスの遵守状況、改善提案を含めてください。

コード:
```python
{code}
```

分析結果を日本語で提供してください。"""
        
        else:  # general
            prompt = f"""以下のPythonコードを総合的に分析してください。
機能、品質、パフォーマンス、セキュリティの観点から評価し、改善提案を含めてください。

コード:
```python
{code}
```

分析結果を日本語で提供してください。"""
        
        return self._generate_content(prompt)
    
    def _generate_documentation(self, code: str, doc_type: str = "README") -> str:
        """
        Generate documentation for code using Gemini.
        """
        if doc_type == "README":
            prompt = f"""以下のPythonコードのREADME.mdを生成してください。
プロジェクト概要、インストール方法、使用方法、API仕様を含めてください。

コード:
```python
{code}
```

Markdown形式で日本語で提供してください。"""
        
        elif doc_type == "API":
            prompt = f"""以下のPythonコードのAPIドキュメントを生成してください。
関数、クラス、メソッドの詳細な説明、パラメータ、戻り値、使用例を含めてください。

コード:
```python
{code}
```

Markdown形式で日本語で提供してください。"""
        
        else:  # general
            prompt = f"""以下のPythonコードのドキュメントを生成してください。
コードの目的、機能、使用方法、注意事項を含めてください。

コード:
```python
{code}
```

Markdown形式で日本語で提供してください。"""
        
        return self._generate_content(prompt)
    
    def _suggest_improvements(self, code: str) -> str:
        """
        Suggest improvements for code using Gemini.
        """
        prompt = f"""以下のPythonコードを改善してください。
現在のコードの問題点を特定し、より良い実装を提案してください。

現在のコード:
```python
{code}
```

改善提案を以下の形式で提供してください:
1. 問題点の特定
2. 改善されたコード
3. 改善の理由

日本語で提供してください。"""
        
        return self._generate_content(prompt)
    
    def execute(self, instruction: str, context: str | None = None, **kwargs) -> str:
        """
        Execute Gemini-related operations based on instruction.
        """
        
        if not self.api_key:
            return "エラー: GEMINI_API_KEYが設定されていません。"
        
        instruction_lower = instruction.lower()
        
        # Extract code from instruction or context
        code = context or ""
        if not code and "code" in kwargs:
            code = kwargs["code"]
        
        # Try to extract code from instruction using regex
        if not code:
            import re
            code_match = re.search(r'code:\s*(.+?)(?:\s|$)', instruction, re.IGNORECASE)
            if code_match:
                code = code_match.group(1).strip()
            else:
                # Try to find code in quotes or backticks
                code_match = re.search(r'["\']([^"\']*def[^"\']*)["\']', instruction)
                if code_match:
                    code = code_match.group(1).strip()
        
        if "analyze" in instruction_lower or "分析" in instruction_lower:
            analysis_type = "general"
            if "security" in instruction_lower or "セキュリティ" in instruction_lower:
                analysis_type = "security"
            elif "performance" in instruction_lower or "パフォーマンス" in instruction_lower:
                analysis_type = "performance"
            elif "quality" in instruction_lower or "品質" in instruction_lower:
                analysis_type = "quality"
            
            if code:
                return self._analyze_code(code, analysis_type)
            else:
                return "エラー: 分析するコードが提供されていません。"
        
        elif "document" in instruction_lower or "ドキュメント" in instruction_lower:
            doc_type = "README"
            if "api" in instruction_lower:
                doc_type = "API"
            
            if code:
                return self._generate_documentation(code, doc_type)
            else:
                return "エラー: ドキュメント化するコードが提供されていません。"
        
        elif "improve" in instruction_lower or "改善" in instruction_lower:
            if code:
                return self._suggest_improvements(code)
            else:
                return "エラー: 改善するコードが提供されていません。"
        
        elif "generate" in instruction_lower or "生成" in instruction_lower:
            # General content generation
            return self._generate_content(instruction)
        
        else:
            return "利用可能なGeminiコマンド: analyze, document, improve, generate"
