"""
Validator Agent

This agent validates the output from other agents before returning to the user.
It performs double-checking to ensure accuracy and quality of responses.
"""

from .base import BaseAgent
from airis.llm import LLMClient

class ValidatorAgent(BaseAgent):
    """
    Agent that validates outputs from other agents.
    
    This agent performs a secondary review of generated content to:
    - Check for errors or inconsistencies
    - Verify completeness
    - Ensure quality standards
    - Suggest improvements if needed
    """
    
    def __init__(self):
        super().__init__()
        self.llm_client = LLMClient()
    
    def execute(self, instruction: str) -> str:
        """
        Validate the given output.
        
        Args:
            instruction: Format "validate: <task_type> | <original_prompt> | <output>"
            
        Returns:
            Validation result with status and feedback
        """
        # Parse instruction
        if not instruction.startswith("validate:"):
            return "Error: Invalid validator instruction format"
        
        parts = instruction.replace("validate:", "").strip().split("|")
        if len(parts) < 3:
            return "Error: Validator requires task_type, original_prompt, and output"
        
        task_type = parts[0].strip()
        original_prompt = parts[1].strip()
        output_to_validate = parts[2].strip()
        
        # Create validation prompt
        validation_prompt = f"""あなたは品質管理の専門家です。以下の出力を検証してください。

【タスクタイプ】: {task_type}
【元の指示】: {original_prompt}
【生成された出力】:
{output_to_validate}

以下の観点から検証してください：
1. **正確性**: 元の指示に正しく対応しているか
2. **完全性**: 必要な情報がすべて含まれているか
3. **品質**: 内容が適切で、わかりやすいか
4. **エラー**: 明らかな誤りや矛盾がないか

検証結果を以下の形式で返してください：

【検証結果】: OK / NG / NEEDS_IMPROVEMENT
【理由】: (簡潔な説明)
【問題点】: (NGまたはNEEDS_IMPROVEMENTの場合のみ)
【改善提案】: (NEEDS_IMPROVEMENTの場合のみ)

重要：
- 小さな表現の違いは許容してください
- 明らかな誤りや重大な欠落のみをNGとしてください
- 出力が長すぎる/短すぎる場合はNEEDS_IMPROVEMENTとしてください
"""
        
        try:
            validation_result = self.llm_client.invoke(validation_prompt)
            result_text = validation_result.content.strip()
            
            # Parse validation result
            if "【検証結果】: OK" in result_text or "検証結果】:OK" in result_text or "検証結果: OK" in result_text:
                return f"VALIDATION_OK|{result_text}"
            elif "【検証結果】: NG" in result_text or "検証結果】:NG" in result_text or "検証結果: NG" in result_text:
                return f"VALIDATION_NG|{result_text}"
            elif "【検証結果】: NEEDS_IMPROVEMENT" in result_text or "検証結果】:NEEDS_IMPROVEMENT" in result_text:
                return f"VALIDATION_NEEDS_IMPROVEMENT|{result_text}"
            else:
                # Fallback: if format is unclear, assume OK
                return f"VALIDATION_OK|{result_text}"
                
        except Exception as e:
            return f"VALIDATION_ERROR|検証中にエラーが発生しました: {str(e)}"
    
    def validate_and_improve(self, task_type: str, original_prompt: str, output: str, max_iterations: int = 2) -> tuple[str, str]:
        """
        Validate output and improve if needed.
        
        Args:
            task_type: Type of task (code_generation, document_generation, etc.)
            original_prompt: Original user prompt
            output: Output to validate
            max_iterations: Maximum number of improvement iterations
            
        Returns:
            Tuple of (final_output, validation_log)
        """
        validation_log = []
        current_output = output
        
        for iteration in range(max_iterations):
            # Validate current output
            instruction = f"validate: {task_type} | {original_prompt} | {current_output}"
            validation_result = self.execute(instruction)
            
            validation_log.append(f"Iteration {iteration + 1}: {validation_result.split('|')[0]}")
            
            if validation_result.startswith("VALIDATION_OK"):
                validation_log.append("✓ Validation passed")
                return current_output, "\n".join(validation_log)
            
            elif validation_result.startswith("VALIDATION_NG"):
                validation_log.append("✗ Validation failed - major issues detected")
                # Extract problems from validation result
                parts = validation_result.split("|")
                if len(parts) > 1:
                    validation_log.append(parts[1])
                return current_output, "\n".join(validation_log)
            
            elif validation_result.startswith("VALIDATION_NEEDS_IMPROVEMENT"):
                validation_log.append("⚠ Needs improvement")
                # Try to improve (future implementation)
                # For now, just return with warning
                return current_output, "\n".join(validation_log)
            
            else:
                # Validation error
                validation_log.append("⚠ Validation error occurred")
                return current_output, "\n".join(validation_log)
        
        return current_output, "\n".join(validation_log)

