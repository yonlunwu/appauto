# README.md
# appauto

一个统一的命令行测试工具，支持 `pytest` 和 `playwright`。

## 安装（开发模式）

```bash
pip install -e .
```

## 使用示例

```bash
appauto run pytest --testpaths testcases/api/test_demo.py -k login --loglevel=info
appauto run ui --testpaths testcases/ui/test_login.spec.ts --loglevel=debug --headless
