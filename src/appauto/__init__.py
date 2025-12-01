import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def get_version() -> str:
    """获取 appauto 版本号

    优先从已安装包的元数据中读取版本（生产环境），
    如果失败则尝试从 pyproject.toml 读取（开发环境）
    """
    # 方法1: 从已安装包的元数据中读取（适用于 pip install 后）
    try:
        if sys.version_info >= (3, 8):
            from importlib.metadata import version
        else:
            from importlib_metadata import version
        return version("appauto")
    except Exception:
        pass

    # 方法2: 从 pyproject.toml 读取（适用于开发环境）
    try:
        root = Path(__file__).resolve().parents[2]
        pyproject_path = root / "pyproject.toml"
        with pyproject_path.open("rb") as f:
            data = tomllib.load(f)
            return data["project"]["version"]
    except Exception:
        pass

    # 如果两种方法都失败，返回默认版本
    return "unknown"


__version__ = get_version()
