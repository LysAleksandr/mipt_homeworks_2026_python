import os
from typing import Any, Dict, Optional
import yaml

def load_config() -> Optional[Dict[str, Any]]:
    config: Dict[str, Any] = {}
    yaml_config: Dict[str, Any] = {}
    if os.path.exists('config.yaml'):
        try:
            with open('config.yaml', 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f) or {}
        except (yaml.YAMLError, OSError):
            pass

    env_map = {
        'api_key': 'API_KEY',
        'api_host': 'API_HOST',
        'model': 'MODEL',
        'limit_message': 'LIMIT_MESSAGE',
        'limit_chars': 'LIMIT_CHARS',
        'temperature': 'TEMPERATURE',
    }
    for key, env_var in env_map.items():
        env_val = os.environ.get(env_var)
        if env_val is not None:
            config[key] = env_val
        elif key in yaml_config:
            config[key] = yaml_config[key]

    if 'system_prompt' in yaml_config:
        config['system_prompt'] = yaml_config['system_prompt']

    if 'api_key' not in config or 'api_host' not in config:
        return None

    if config.get('limit_message') is not None:
        config['limit_message'] = int(config['limit_message'])
    else:
        config['limit_message'] = None

    if config.get('limit_chars') is not None:
        config['limit_chars'] = int(config['limit_chars'])
    else:
        config['limit_chars'] = None

    temp = config.get('temperature')
    if temp is not None:
        try:
            config['temperature'] = float(temp)
        except (ValueError, TypeError):
            config['temperature'] = 0.7
    else:
        config['temperature'] = 0.7

    config.setdefault('model', 'gemma3:270m')
    config.setdefault('system_prompt', 'You are a helpful assistant.')

    if config['limit_message'] is not None and config['limit_message'] < 0:
        config['limit_message'] = 0
    if config['limit_chars'] is not None and config['limit_chars'] < 0:
        config['limit_chars'] = 0

    return config