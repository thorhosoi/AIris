"""
AI Engine Selection Manager

This module manages the selection and routing of AI engines based on configuration,
compliance requirements, and cost optimization settings.
"""

from typing import Dict, List, Optional, Any
from airis.config import config
import logging

logger = logging.getLogger(__name__)

class AIEngineManager:
    """
    Manages AI engine selection and routing based on configuration.
    """
    
    def __init__(self):
        self.config = config
        self._load_configuration()
    
    def _load_configuration(self):
        """Load AI engine configuration from config.yaml"""
        # Reload config from file to get latest settings
        self.config.settings = self.config._load_config()
        
        self.default_engine = self.config.get("ai_engines.default_engine", "claude")
        self.task_routing = self.config.get("ai_engines.task_routing", {})
        self.compliance_mode = self.config.get("ai_engines.compliance_mode", False)
        self.allowed_engines = self.config.get("ai_engines.allowed_engines", [])
        self.cost_optimization = self.config.get("ai_engines.cost_optimization", False)
        self.cost_preferences = self.config.get("ai_engines.cost_preferences", {})
        
        # Engine availability mapping
        self.engine_availability = {
            "claude": True,
            "gemini": True,
            "cursor": True,
            "web_search": True,
            "web_browser": True,
            "local": True
        }
    
    def get_engine_for_task(self, task_type: str, user_prompt: str = "") -> str:
        """
        Determine the best AI engine for a given task.
        
        Args:
            task_type: Type of task (code_generation, document_generation, etc.)
            user_prompt: User's prompt for additional context
            
        Returns:
            Selected engine name
        """
        # Reload configuration to get latest settings
        self._load_configuration()
        # Check compliance mode first
        if self.compliance_mode:
            return self._get_compliant_engine(task_type, user_prompt)
        
        # Check cost optimization mode
        if self.cost_optimization:
            return self._get_cost_optimized_engine(task_type, user_prompt)
        
        # Use task-specific routing
        if task_type in self.task_routing:
            engine = self.task_routing[task_type]
            if self._is_engine_available(engine):
                return engine
        
        # Fallback to default engine
        if self._is_engine_available(self.default_engine):
            return self.default_engine
        
        # Last resort: find any available engine
        for engine in self.engine_availability:
            if self.engine_availability[engine]:
                return engine
        
        return "claude"  # Ultimate fallback
    
    def _get_compliant_engine(self, task_type: str, user_prompt: str) -> str:
        """Get engine that complies with corporate policies."""
        # Filter available engines by compliance
        compliant_engines = [eng for eng in self.allowed_engines 
                           if self._is_engine_available(eng)]
        
        if not compliant_engines:
            logger.warning("No compliant engines available, using default")
            return self.default_engine
        
        # Try task-specific routing first
        if task_type in self.task_routing:
            preferred_engine = self.task_routing[task_type]
            if preferred_engine in compliant_engines:
                return preferred_engine
        
        # Return first compliant engine
        return compliant_engines[0]
    
    def _get_cost_optimized_engine(self, task_type: str, user_prompt: str) -> str:
        """Get engine optimized for cost."""
        # Determine task complexity for cost optimization
        complexity = self._assess_task_complexity(user_prompt)
        
        if complexity == "high":
            return self.cost_preferences.get("high_cost", "claude")
        elif complexity == "medium":
            return self.cost_preferences.get("medium_cost", "gemini")
        elif complexity == "low":
            return self.cost_preferences.get("low_cost", "web_search")
        else:
            return self.cost_preferences.get("free", "local")
    
    def _assess_task_complexity(self, user_prompt: str) -> str:
        """Assess task complexity based on prompt content."""
        prompt_lower = user_prompt.lower()
        
        # High complexity indicators
        high_complexity_keywords = [
            "complex", "advanced", "sophisticated", "enterprise", "production",
            "複雑", "高度", "本格的", "エンタープライズ", "本番"
        ]
        
        # Medium complexity indicators
        medium_complexity_keywords = [
            "analysis", "optimize", "improve", "refactor", "debug",
            "分析", "最適化", "改善", "リファクタリング", "デバッグ"
        ]
        
        # Low complexity indicators
        low_complexity_keywords = [
            "simple", "basic", "quick", "small", "test",
            "簡単", "基本", "クイック", "小さな", "テスト"
        ]
        
        if any(keyword in prompt_lower for keyword in high_complexity_keywords):
            return "high"
        elif any(keyword in prompt_lower for keyword in medium_complexity_keywords):
            return "medium"
        elif any(keyword in prompt_lower for keyword in low_complexity_keywords):
            return "low"
        else:
            return "medium"  # Default to medium complexity
    
    def _is_engine_available(self, engine: str) -> bool:
        """Check if an engine is available and properly configured."""
        if not self.engine_availability.get(engine, False):
            return False
        
        # Check specific engine requirements
        if engine == "claude":
            return self._check_claude_availability()
        elif engine == "gemini":
            return self._check_gemini_availability()
        elif engine == "cursor":
            return self._check_cursor_availability()
        elif engine in ["web_search", "web_browser"]:
            return True  # These are always available
        elif engine == "local":
            return True  # Local operations are always available
        
        return True
    
    def _check_claude_availability(self) -> bool:
        """Check if Claude is available."""
        try:
            import os
            return bool(os.environ.get("ANTHROPIC_API_KEY"))
        except:
            return False
    
    def _check_gemini_availability(self) -> bool:
        """Check if Gemini is available."""
        try:
            import os
            return bool(os.environ.get("GEMINI_API_KEY"))
        except:
            return False
    
    def _check_cursor_availability(self) -> bool:
        """Check if Cursor is available."""
        try:
            import shutil
            cursor_path = self.config.get("cursor.path", "cursor")
            return shutil.which(cursor_path) is not None
        except:
            return False
    
    def set_engine_availability(self, engine: str, available: bool):
        """Set the availability of an engine."""
        self.engine_availability[engine] = available
        logger.info(f"Engine {engine} availability set to {available}")
    
    def get_available_engines(self) -> List[str]:
        """Get list of currently available engines."""
        return [engine for engine, available in self.engine_availability.items() 
                if available and self._is_engine_available(engine)]
    
    def set_compliance_mode(self, enabled: bool, allowed_engines: List[str] = None):
        """Enable/disable compliance mode with allowed engines."""
        self.compliance_mode = enabled
        if allowed_engines:
            self.allowed_engines = allowed_engines
        logger.info(f"Compliance mode {'enabled' if enabled else 'disabled'}")
    
    def set_cost_optimization(self, enabled: bool, preferences: Dict[str, str] = None):
        """Enable/disable cost optimization mode."""
        self.cost_optimization = enabled
        if preferences:
            self.cost_preferences.update(preferences)
        logger.info(f"Cost optimization {'enabled' if enabled else 'disabled'}")
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get information about all engines."""
        # Reload configuration to get latest settings
        self._load_configuration()
        return {
            "default_engine": self.default_engine,
            "available_engines": self.get_available_engines(),
            "compliance_mode": self.compliance_mode,
            "cost_optimization": self.cost_optimization,
            "task_routing": self.task_routing,
            "engine_availability": self.engine_availability
        }

# Global instance
ai_engine_manager = AIEngineManager()
