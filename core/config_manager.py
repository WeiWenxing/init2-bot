import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import threading


DEFAULT_CONFIG: Dict[str, Any] = {
    "initial_points": 100,
    "invite_points": 50,
}


class ConfigManager:
    """
    提供内存缓存与持久化的配置管理器，支持快速读取与动态更新。
    """

    def __init__(self, file_path: Path, defaults: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化配置管理器

        Args:
            file_path: 配置文件路径
            defaults: 默认配置字典
        """
        self._file_path = file_path
        self._defaults = defaults or {}
        self._lock = threading.Lock()
        self._cache: Dict[str, Any] = {}
        self._ensure_dirs()
        self._load()

    def _ensure_dirs(self) -> None:
        """
        确保配置文件所在目录存在
        """
        self._file_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> None:
        """
        从磁盘加载配置到内存缓存，如文件不存在则创建并写入默认值
        """
        with self._lock:
            if not self._file_path.exists():
                self._cache = dict(self._defaults)
                self._atomic_write(self._cache)
                return
            try:
                content = self._file_path.read_text(encoding="utf-8")
                data = json.loads(content) if content.strip() else {}
            except Exception:
                data = {}
            merged = dict(self._defaults)
            merged.update(data)
            self._cache = merged

    def _atomic_write(self, data: Dict[str, Any]) -> None:
        """
        原子写入配置文件，避免写入过程中损坏

        Args:
            data: 要写入的配置字典
        """
        temp_path = self._file_path.with_suffix(self._file_path.suffix + ".tmp")
        temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_path.replace(self._file_path)

    def save(self) -> None:
        """
        将当前缓存写入磁盘
        """
        with self._lock:
            self._atomic_write(self._cache)

    def reload(self) -> None:
        """
        从磁盘重新加载到缓存
        """
        self._load()

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """
        读取配置项

        Args:
            key: 配置键
            default: 若不存在时的返回值

        Returns:
            配置值或默认值
        """
        return self._cache.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        设置单个配置项并持久化

        Args:
            key: 配置键
            value: 配置值
        """
        with self._lock:
            self._cache[key] = value
            self._atomic_write(self._cache)

    def update(self, values: Dict[str, Any]) -> None:
        """
        批量更新配置并持久化

        Args:
            values: 要更新的键值对
        """
        with self._lock:
            self._cache.update(values)
            self._atomic_write(self._cache)

    def remove(self, key: str) -> None:
        """
        删除配置项并持久化

        Args:
            key: 配置键
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._atomic_write(self._cache)

    def all(self) -> Dict[str, Any]:
        """
        返回当前所有配置的副本

        Returns:
            配置字典副本
        """
        return dict(self._cache)

    @property
    def file_path(self) -> Path:
        """
        返回配置文件路径
        """
        return self._file_path


_config_singleton: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """
    获取配置管理器单例，如果不存在则按默认路径创建

    Returns:
        ConfigManager 实例
    """
    global _config_singleton
    if _config_singleton is None:
        file_from_env = os.environ.get("SETTINGS_FILE")
        if file_from_env:
            path = Path(file_from_env)
        else:
            path = Path("storage/config/settings.json")
        _config_singleton = ConfigManager(path, DEFAULT_CONFIG)
    return _config_singleton

