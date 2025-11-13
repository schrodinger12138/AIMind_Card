"""配置管理模块 - 统一管理API密钥、代理等配置"""
import os
import json
from typing import Optional, Dict, Any

# 导入默认配置
try:
    from ai_reader_cards.config import (
        API_BASE, OPENAI_API_KEY, DEFAULT_MODEL, AVAILABLE_MODELS,
        USE_PROXY, DEFAULT_PROXIES, WHEN_TO_USE_PROXY,
        DEFAULT_LAYOUT, DEFAULT_CONNECTION_STYLE,
        DEFAULT_TARGET_LANGUAGE, MAX_TOKEN_LIMIT
    )
except ImportError:
    # 如果config.py不存在，使用默认值
    API_BASE = "https://api.chatanywhere.tech/v1"
    OPENAI_API_KEY = ""
    DEFAULT_MODEL = "gpt-3.5-turbo"
    AVAILABLE_MODELS = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]
    USE_PROXY = False
    DEFAULT_PROXIES = {"http": None, "https": None}
    WHEN_TO_USE_PROXY = ["translate", "api_request"]
    DEFAULT_LAYOUT = "mind_map"
    DEFAULT_CONNECTION_STYLE = "fixed"
    DEFAULT_TARGET_LANGUAGE = "zh"
    MAX_TOKEN_LIMIT = 2048


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "api": {
                "openai_api_key": os.environ.get("OPENAI_API_KEY", OPENAI_API_KEY),
                "openai_base_url": os.environ.get("OPENAI_BASE_URL", API_BASE),
                "model": DEFAULT_MODEL,
                "deepseek_api_key": os.environ.get("DEEPSEEK_API_KEY", ""),
                "deepseek_base_url": os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1/chat/completions"),
                "deepseek_model": "deepseek-chat"
            },
            "proxy": {
                "use_proxy": USE_PROXY,
                "proxies": DEFAULT_PROXIES.copy(),
                "when_to_use_proxy": WHEN_TO_USE_PROXY.copy()
            },
            "translation": {
                "default_target_language": DEFAULT_TARGET_LANGUAGE,
                "preserve_markdown": True,
                "max_token_limit": MAX_TOKEN_LIMIT
            },
            "layout": {
                "default": DEFAULT_LAYOUT
            },
            "connection": {
                "default": DEFAULT_CONNECTION_STYLE
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并配置
                    self._merge_config(default_config, user_config)
            except Exception as e:
                print(f"加载配置文件失败: {e}，使用默认配置")
        
        return default_config
    
    def _merge_config(self, default: Dict, user: Dict):
        """递归合并配置"""
        for key, value in user.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key_path: str, default=None):
        """
        获取配置值
        
        Args:
            key_path: 配置路径，如 "api.openai_api_key"
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, key_path: str, value: Any):
        """
        设置配置值
        
        Args:
            key_path: 配置路径，如 "api.openai_api_key"
            value: 配置值
        """
        keys = key_path.split('.')
        config = self.config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
    
    def get_proxies(self, task: str = None) -> Optional[Dict[str, str]]:
        """
        获取代理配置
        
        Args:
            task: 任务类型，用于判断是否需要使用代理
            
        Returns:
            代理配置字典，如果不需要代理则返回None
        """
        use_proxy = self.get("proxy.use_proxy", False)
        if not use_proxy:
            return None
        
        # 检查任务是否需要代理
        if task:
            when_to_use = self.get("proxy.when_to_use_proxy", [])
            if task not in when_to_use:
                return None
        
        proxies = self.get("proxy.proxies", {})
        http_proxy = proxies.get("http")
        https_proxy = proxies.get("https")
        
        if not http_proxy and not https_proxy:
            return None
        
        result = {}
        if http_proxy:
            result["http"] = http_proxy
        if https_proxy:
            result["https"] = https_proxy
        
        return result if result else None
    
    def get_openai_config(self) -> Dict[str, Any]:
        """获取OpenAI API配置"""
        return {
            "api_key": self.get("api.openai_api_key", ""),
            "base_url": self.get("api.openai_base_url", "https://api.chatanywhere.tech/v1"),
            "model": self.get("api.model", "gpt-3.5-turbo")
        }
    
    def get_deepseek_config(self) -> Dict[str, Any]:
        """获取DeepSeek API配置"""
        return {
            "api_key": self.get("api.deepseek_api_key", ""),
            "base_url": self.get("api.deepseek_base_url", "https://api.deepseek.com/v1/chat/completions"),
            "model": self.get("api.deepseek_model", "deepseek-chat")
        }


# 全局配置管理器实例
_config_manager = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

