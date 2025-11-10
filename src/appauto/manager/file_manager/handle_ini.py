import configparser
from pathlib import Path
from typing import Optional, Dict, Any


class IniHandler(object):
    """INI 文件处理类"""

    def __init__(self, file_path: Optional[Path] = None):
        self.file_path = file_path
        # 禁用插值功能，避免 % 字符导致的问题
        self.config = configparser.ConfigParser(interpolation=None)
        if file_path and file_path.exists():
            self.config.read(file_path)

    def add_section(self, section: str, options: Dict[str, Any]) -> None:
        """添加配置节"""
        if not self.config.has_section(section):
            self.config.add_section(section)

        for key, value in options.items():
            self.config.set(section, key, str(value))

    def write(self) -> None:
        """写入配置文件"""
        if not self.file_path:
            raise ValueError("File path not set")

        with open(self.file_path, "w", encoding="utf-8") as f:
            self.config.write(f)

    def remove(self) -> None:
        """删除配置文件"""
        if self.file_path and self.file_path.exists():
            self.file_path.unlink()

    def get_section(self, section: str) -> Optional[Dict[str, str]]:
        """获取指定节的配置"""
        if self.config.has_section(section):
            return dict(self.config.items(section))
