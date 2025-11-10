import yaml
from jinja2 import Template
from pathlib import Path
from addict import Dict as ADDict
from typing import Optional, Union, Dict, Any


class YMLHandler:
    """YAML / Jinja2-YAML 文件操作类"""

    def __init__(self, file_path: Union[str, Path], variables: Optional[Dict[str, Any]] = None):
        self.file_path = Path(file_path)
        self.variables = variables or {}
        self.data: ADDict = self._load()

    def _load(self) -> ADDict:
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        content = self.file_path.read_text(encoding="utf-8")

        if self.file_path.suffixes[-2:] == [".yml", ".j2"]:
            # 是 .yml.j2 模板
            template = Template(content)
            rendered = template.render(**self.variables)
            return ADDict(yaml.safe_load(rendered) or {})

        # 普通 yml 文件
        return ADDict(yaml.safe_load(content) or {})

    def write(self, output_path: Optional[Union[str, Path]] = None) -> None:
        """默认将 self.data 写入 YAML 文件"""
        target = Path(output_path) if output_path else self.file_path
        with open(target, "w", encoding="utf-8") as f:
            # TODO 这里只换了顶层, 没有逐层替换
            yaml.safe_dump(self._to_dict(self.data), f, allow_unicode=True, sort_keys=False)

    def as_dict(self) -> dict:
        """以原始 dict 返回数据"""
        return self._to_dict(self.data)

    def _to_dict(self, obj: Any) -> Any:
        """递归将 self.data(addict.Dict) 转换为标准 dict"""
        if isinstance(obj, dict):
            return {k: self._to_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._to_dict(i) for i in obj]
        else:
            return obj

    def delete_key(self, key_: str = None, default=None):
        """从 self.data 移除某个 key, 如果 key 不存在则返回 default(None)"""
        if not key_:
            return

        return self.data.pop(key_, default)
