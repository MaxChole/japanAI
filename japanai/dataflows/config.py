"""
Dataflows 全局配置：当前使用的数据源等。
由主图初始化时 set_config(config)，各 dataflows 通过 get_config() 读取。
"""
from typing import Any, Dict

_config: Dict[str, Any] = {}


def get_config() -> Dict[str, Any]:
    """返回当前配置的副本。"""
    return dict(_config)


def set_config(config: Dict[str, Any]) -> None:
    """注入配置（通常来自 RealEstateGraph 的 config）。"""
    global _config
    _config = config if config is not None else {}
