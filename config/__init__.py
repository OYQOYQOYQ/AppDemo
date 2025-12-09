import json
import os

# 加载默认配置
_config_path = os.path.join(os.path.dirname(__file__), 'default_config.json')
default_config = {}

if os.path.exists(_config_path):
    with open(_config_path, 'r', encoding='utf-8') as f:
        default_config = json.load(f)

__all__ = ['default_config']