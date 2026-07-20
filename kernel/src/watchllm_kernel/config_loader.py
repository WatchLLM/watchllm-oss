import os
import yaml
from typing import Any, Dict, Optional

CONFIG_FILENAME = ".watchllm.yaml"

def find_config(start_path: str = ".") -> Optional[str]:
    """Search for .watchllm.yaml starting from start_path and moving upwards."""
    current_path = os.path.abspath(start_path)
    
    while True:
        potential_config = os.path.join(current_path, CONFIG_FILENAME)
        if os.path.isfile(potential_config):
            return potential_config
            
        parent = os.path.dirname(current_path)
        if parent == current_path:
            break
        current_path = parent
        
    return None

def load_config(config_path: Optional[str] = None, start_path: str = ".") -> Dict[str, Any]:
    """Load the WatchLLM configuration from the given path or auto-discover it."""
    if not config_path:
        config_path = find_config(start_path)
        
    if not config_path or not os.path.isfile(config_path):
        return {}
        
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            return config if config else {}
    except Exception as e:
        print(f"Warning: Failed to load config from {config_path}: {e}")
        return {}

def get_rule_config(config: Dict[str, Any], rule_name: str) -> Dict[str, Any]:
    """Extract configuration for a specific rule."""
    if not config or "rules" not in config or not config["rules"]:
        return {}
    return config["rules"].get(rule_name, {})
