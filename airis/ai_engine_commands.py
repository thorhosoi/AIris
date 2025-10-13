"""
AI Engine Selection Commands

This module provides commands for managing AI engine selection and configuration.
"""

from airis.ai_engine_manager import ai_engine_manager
from airis.config import config
import yaml
import os

class AIEngineCommands:
    """Commands for managing AI engine selection."""
    
    @staticmethod
    def set_default_engine(engine: str) -> str:
        """Set the default AI engine."""
        if engine not in ai_engine_manager.get_available_engines():
            return f"Error: Engine '{engine}' is not available. Available engines: {ai_engine_manager.get_available_engines()}"
        
        # Update config
        config.set("ai_engines.default_engine", engine)
        ai_engine_manager.default_engine = engine
        
        return f"Default engine set to: {engine}"
    
    @staticmethod
    def set_task_routing(task_type: str, engine: str) -> str:
        """Set engine for specific task type."""
        if engine not in ai_engine_manager.get_available_engines():
            return f"Error: Engine '{engine}' is not available. Available engines: {ai_engine_manager.get_available_engines()}"
        
        # Update config
        task_routing = config.get("ai_engines.task_routing", {})
        task_routing[task_type] = engine
        config.set("ai_engines.task_routing", task_routing)
        ai_engine_manager.task_routing[task_type] = engine
        
        return f"Task '{task_type}' now uses engine: {engine}"
    
    @staticmethod
    def enable_compliance_mode(allowed_engines: list = None) -> str:
        """Enable compliance mode with allowed engines."""
        if allowed_engines is None:
            allowed_engines = ["claude", "gemini", "local"]
        
        # Validate engines
        available_engines = ai_engine_manager.get_available_engines()
        invalid_engines = [eng for eng in allowed_engines if eng not in available_engines]
        
        if invalid_engines:
            return f"Error: Invalid engines: {invalid_engines}. Available engines: {available_engines}"
        
        # Update config
        config.set("ai_engines.compliance_mode", True)
        config.set("ai_engines.allowed_engines", allowed_engines)
        ai_engine_manager.set_compliance_mode(True, allowed_engines)
        
        return f"Compliance mode enabled. Allowed engines: {allowed_engines}"
    
    @staticmethod
    def disable_compliance_mode() -> str:
        """Disable compliance mode."""
        config.set("ai_engines.compliance_mode", False)
        ai_engine_manager.set_compliance_mode(False)
        
        return "Compliance mode disabled"
    
    @staticmethod
    def enable_cost_optimization(preferences: dict = None) -> str:
        """Enable cost optimization mode."""
        if preferences is None:
            preferences = {
                "high_cost": "claude",
                "medium_cost": "gemini", 
                "low_cost": "web_search",
                "free": "local"
            }
        
        # Update config
        config.set("ai_engines.cost_optimization", True)
        config.set("ai_engines.cost_preferences", preferences)
        ai_engine_manager.set_cost_optimization(True, preferences)
        
        return f"Cost optimization enabled. Preferences: {preferences}"
    
    @staticmethod
    def disable_cost_optimization() -> str:
        """Disable cost optimization mode."""
        config.set("ai_engines.cost_optimization", False)
        ai_engine_manager.set_cost_optimization(False)
        
        return "Cost optimization disabled"
    
    @staticmethod
    def set_engine_availability(engine: str, available: bool) -> str:
        """Set engine availability."""
        ai_engine_manager.set_engine_availability(engine, available)
        
        return f"Engine '{engine}' availability set to: {available}"
    
    @staticmethod
    def get_engine_info() -> str:
        """Get information about all engines."""
        info = ai_engine_manager.get_engine_info()
        
        result = "=== AI Engine Information ===\n"
        result += f"Default Engine: {info['default_engine']}\n"
        result += f"Available Engines: {', '.join(info['available_engines'])}\n"
        result += f"Compliance Mode: {info['compliance_mode']}\n"
        result += f"Cost Optimization: {info['cost_optimization']}\n\n"
        
        result += "Task Routing:\n"
        for task, engine in info['task_routing'].items():
            result += f"  {task}: {engine}\n"
        
        result += "\nEngine Availability:\n"
        for engine, available in info['engine_availability'].items():
            status = "✓" if available else "✗"
            result += f"  {engine}: {status}\n"
        
        return result
    
    @staticmethod
    def save_config() -> str:
        """Save current configuration to config.yaml."""
        try:
            # Get current config
            current_config = config.settings
            
            # Write to file
            config_path = "config.yaml"
            with open(config_path, 'w') as f:
                yaml.dump(current_config, f, default_flow_style=False, allow_unicode=True)
            
            return f"Configuration saved to {config_path}"
        except Exception as e:
            return f"Error saving configuration: {e}"
    
    @staticmethod
    def debug_config() -> str:
        """Debug configuration loading."""
        import yaml
        
        # Read config file directly
        with open("config.yaml", 'r') as f:
            file_config = yaml.safe_load(f)
        
        # Get config from Config object
        config_obj = config.settings
        
        result = "=== Debug Configuration ===\n\n"
        result += "File config.yaml:\n"
        result += f"  default_engine: {file_config.get('ai_engines', {}).get('default_engine')}\n"
        result += f"  document_generation: {file_config.get('ai_engines', {}).get('task_routing', {}).get('document_generation')}\n\n"
        
        result += "Config object:\n"
        result += f"  default_engine: {config.get('ai_engines.default_engine')}\n"
        result += f"  document_generation: {config.get('ai_engines.task_routing.document_generation')}\n\n"
        
        result += "AIEngineManager:\n"
        result += f"  default_engine: {ai_engine_manager.default_engine}\n"
        result += f"  document_generation: {ai_engine_manager.task_routing.get('document_generation')}\n"
        
        return result
    
    @staticmethod
    def reset_to_defaults() -> str:
        """Reset AI engine configuration to defaults."""
        default_config = {
            "ai_engines": {
                "default_engine": "claude",
                "task_routing": {
                    "code_generation": "cursor",
                    "document_generation": "claude",
                    "code_analysis": "gemini",
                    "web_search": "web_search",
                    "web_browsing": "web_browser",
                    "git_operations": "local",
                    "shell_operations": "local"
                },
                "compliance_mode": False,
                "allowed_engines": ["claude", "gemini", "cursor", "web_search", "web_browser", "local"],
                "cost_optimization": False,
                "cost_preferences": {
                    "high_cost": "claude",
                    "medium_cost": "gemini",
                    "low_cost": "web_search",
                    "free": "local"
                }
            }
        }
        
        # Update config
        for key, value in default_config.items():
            config.set(key, value)
        
        # Reload AI engine manager
        ai_engine_manager._load_configuration()
        
        return "AI engine configuration reset to defaults"

# Global instance
ai_engine_commands = AIEngineCommands()
