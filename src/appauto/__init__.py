import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def get_version() -> str:
    # 当前文件路径：src/appauto/__init__.py
    # 向上两级 -> 项目根目录
    root = Path(__file__).resolve().parents[2]  # 从 __init__.py 向上两级
    pyproject_path = root / "pyproject.toml"

    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)
        return data["project"]["version"]


__version__ = get_version()
