import json
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    配置管理器
    负责加载、保存和管理应用程序配置
    """
    
    def __init__(self, config_file="config.json"):
        """
        初始化配置管理器
        
        Args:
            config_file (str): 配置文件路径
        """
        self.config_file = config_file
        self._config = self._load_default_config()
        self.load_config()
    
    def _load_default_config(self):
        """
        加载默认配置
        首先尝试从配置文件加载，如果不存在则使用硬编码的默认值
        
        Returns:
            dict: 默认配置字典
        """
        # 默认配置文件路径
        default_config_path = Path(__file__).parent.parent / "config" / "default_config.json"
        
        try:
            if default_config_path.exists():
                with open(default_config_path, 'r', encoding='utf-8') as f:
                    logger.info(f"Loading default configuration from {default_config_path}")
                    return json.load(f)
            else:
                logger.warning(f"Default config file not found: {default_config_path}")
        except Exception as e:
            logger.error(f"Failed to load default configuration file: {str(e)}")
        
        # 硬编码的默认配置作为后备
        return {
            "app_name": "Mini App",
            "version": "1.0.0",
            "window_size": {
                "width": 200,
                "height": 200
            },
            "window_position": {
                "x": 100,
                "y": 100
            },
            "theme": "default",
            "log_level": "INFO"
        }
    def load_config(self):
        """
        从配置文件加载配置
        
        Returns:
            bool: 是否成功加载配置
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    # 更新默认配置
                    self._config.update(file_config)
                logger.info(f"Configuration loaded from {self.config_file}")
                return True
            else:
                logger.warning(f"Config file not found: {self.config_file}. Using default configuration.")
                # 可以选择保存默认配置
                self.save_config()
                return False
        except Exception as e:
            logger.error(f"Failed to load configuration: {str(e)}")
            return False
    
    def save_config(self):
        """
        保存配置到文件
        
        Returns:
            bool: 是否成功保存配置
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            logger.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
            return False
    
    def get(self, key, default=None):
        """
        获取配置值
        
        Args:
            key (str): 配置键名，可以使用点号分隔嵌套键，如 "window_size.width"
            default: 默认值，如果键不存在则返回
            
        Returns:
            配置值或默认值
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key, value):
        """
        设置配置值
        
        Args:
            key (str): 配置键名，可以使用点号分隔嵌套键
            value: 配置值
            
        Returns:
            bool: 是否成功设置配置
        """
        keys = key.split('.')
        config = self._config
        
        try:
            # 导航到目标键的父级
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # 设置值
            config[keys[-1]] = value
            logger.info(f"Configuration updated: {key} = {value}")
            return True
        except Exception as e:
            logger.error(f"Failed to update configuration: {str(e)}")
            return False
    
    def get_all(self):
        """
        获取所有配置
        
        Returns:
            dict: 完整的配置字典
        """
        return self._config.copy()
    
    def update(self, config_dict):
        """
        批量更新配置
        
        Args:
            config_dict (dict): 配置字典
            
        Returns:
            bool: 是否成功更新配置
        """
        try:
            self._config.update(config_dict)
            logger.info(f"Configuration updated with {len(config_dict)} items")
            return True
        except Exception as e:
            logger.error(f"Failed to update configuration: {str(e)}")
            return False