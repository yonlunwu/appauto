import json
from pathlib import Path
from typing import Union, List
from addict import Dict as ADDict


class HandleJsonl:
    """JSONL 文件加载类"""

    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        self.data: List[ADDict] = self._load()

    def _load(self) -> List[ADDict]:
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        result = []
        with self.file_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    result.append(ADDict(obj))
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSONL line: {line}\nError: {e}")
        return result
