# appauto 打包与分发指南

本文档详细说明如何将 appauto 打包成 wheel 格式，以便在其他项目中安装和使用。

## 目录

1. [项目概述](#项目概述)
2. [打包前准备](#打包前准备)
3. [构建 Wheel 包](#构建-wheel-包)
4. [安装 Wheel 包](#安装-wheel-包)
5. [使用方式](#使用方式)
6. [常见问题](#常见问题)

---

## 项目概述

appauto 是一个统一的命令行测试工具，支持以下功能：

- **测试框架**: 支持 pytest 和 playwright
- **环境部署**: 支持 AMaaS、zhiwen-ft 等环境的自动化部署
- **性能测试**: 基于 evalscope 的模型性能测试
- **命令行工具**: 提供完整的 CLI 接口
- **Python API**: 提供可编程的 Python API

**版本信息**: 当前版本为 `0.1.1`（定义在 `pyproject.toml` 中）

---

## 打包前准备

### 1. 确认项目配置

项目使用 `pyproject.toml` 作为配置文件，采用 `pdm-backend` 作为构建后端。

关键配置项：

```toml
[project]
name = "appauto"
version = "0.1.1"
requires-python = ">=3.10"

[project.scripts]
appauto = "appauto.cli:cli"

[build-system]
requires = ["pdm-backend"]
build-backend = "pdm.backend"
```

### 2. 确保环境满足要求

- Python 版本: >= 3.10
- 安装构建工具:

```bash
pip install build pdm-backend
```

### 3. 检查项目结构

```
appauto/
├── pyproject.toml          # 项目配置文件
├── README.md               # 项目说明
├── src/
│   └── appauto/           # 源代码目录
│       ├── __init__.py    # 包初始化文件（含版本信息）
│       ├── cli.py         # CLI 入口点
│       ├── manager/       # 各类管理器
│       ├── operator/      # 操作器
│       ├── tool/          # 工具集
│       └── ...
├── scripts/               # 脚本文件
└── testcases/            # 测试用例
```

---

## 构建 Wheel 包

### 方法一：使用 Python Build 模块（推荐）

这是标准的 Python 打包方式，适用于所有符合 PEP 517/518 规范的项目。

```bash
# 在项目根目录执行
python -m build
```

构建完成后，wheel 文件会生成在 `dist/` 目录下：

```
dist/
├── appauto-0.1.1-py3-none-any.whl    # Wheel 包
└── appauto-0.1.1.tar.gz              # 源码包（可选）
```

### 方法二：使用 PDM 工具

如果你使用 PDM 作为项目管理工具：

```bash
# 安装 pdm
pip install pdm

# 构建 wheel 包
pdm build
```

### 构建参数说明

**仅构建 wheel 包**（不构建源码包）:

```bash
python -m build --wheel
```

**仅构建源码包**:

```bash
python -m build --sdist
```

**清理旧的构建产物**:

```bash
rm -rf dist/ build/ *.egg-info .pdm-build/
python -m build
```

---

## 安装 Wheel 包

### 1. 直接安装本地 wheel 包

```bash
pip install /path/to/appauto-0.1.1-py3-none-any.whl
```

### 2. 从服务器路径安装

假设你已将 wheel 包上传到服务器路径 `/mnt/data/packages/`：

```bash
# SSH 方式
pip install root@server:/mnt/data/packages/appauto-0.1.1-py3-none-any.whl

# HTTP 服务器方式
pip install http://your-server.com/packages/appauto-0.1.1-py3-none-any.whl
```

### 3. 使用 requirements.txt

在 `requirements.txt` 中指定：

```txt
# 本地文件
appauto @ file:///path/to/appauto-0.1.1-py3-none-any.whl

# 或者通过 HTTP
appauto @ http://your-server.com/packages/appauto-0.1.1-py3-none-any.whl
```

然后安装：

```bash
pip install -r requirements.txt
```

### 4. 验证安装

```bash
# 查看安装的版本
pip show appauto

# 验证命令行工具
appauto --version

# 验证 Python API
python -c "import appauto; print(appauto.__version__)"
```

---

## 使用方式

### 1. 命令行工具（CLI）使用

安装 wheel 包后，`appauto` 命令会自动注册到系统路径中。

#### 查看帮助信息

```bash
appauto --help
```

#### 运行测试

**运行 pytest 测试**:

```bash
appauto run pytest \
    --testpaths testcases/demo/test_appauto_demo.py \
    --case-level smoke \
    --log-level INFO
```

**运行 UI 测试**:

```bash
appauto run ui --testpaths testcases/ui/
```

#### 环境部署

**部署 AMaaS**:

```bash
appauto env deploy amaas \
    --ip 192.168.1.100 \
    --ssh-user admin \
    --ssh-password yourpassword \
    --tag v3.3.1 \
    --tar-name amaas-v3.3.1.tar.gz
```

**部署 zhiwen-ft**:

```bash
appauto env deploy ft \
    --ip 192.168.1.100 \
    --ssh-user admin \
    --ssh-password yourpassword \
    --tag 3.3.2rc1.post1 \
    --tar-name ft-3.3.2rc1.post1.tar.gz
```

#### 性能测试（Benchmark）

**基于 evalscope 运行性能测试**:

```bash
appauto bench evalscope perf \
    --base-amaas \
    --ip 192.168.110.15 \
    --port 10011 \
    --model DeepSeek-R1-0528-GPU-weight \
    --tp 4 \
    --parallel "1 4 8" \
    --number "5" \
    --input-length 128 \
    --output-length 512
```

### 2. Python API 使用

安装 wheel 包后，可以在 Python 代码中导入和使用 appauto 的各个模块。

#### 基本导入

```python
import appauto
from appauto.manager.config_manager import LoggingConfig, PytestConfig
from appauto.runners.pytest_runner import PytestRunner
```

#### 使用管理器

**配置日志**:

```python
from appauto.manager.config_manager import LoggingConfig

# 配置日志
LoggingConfig.config_logging(log_level="INFO", timestamp="20250101_120000")
logger = LoggingConfig.get_logger()
logger.info("开始执行任务")
```

**配置测试环境**:

```python
from appauto.manager.config_manager import TestDataConfig

TestDataConfig().config_testdata(
    mode="pytest",
    testpaths="testcases/",
    log_level="INFO",
    timestamp="20250101_120000"
)
```

#### 使用组件管理器

**管理 AMaaS 组件**:

```python
from appauto.operator.amaas_node import AMaaSNode

# 连接到 AMaaS 节点
amaas = AMaaSNode(
    ip="192.168.110.15",
    ssh_user="admin",
    ssh_password="password",
    ssh_port=22
)

# 获取模型列表
models = amaas.api.init_model_store.llm.filter(name="DeepSeek-R1")

# 启动模型
amaas.api.launch_model_with_perf(
    tp=4,
    model_store=models[0],
    model_name="DeepSeek-R1",
    timeout=900
)
```

**使用 Docker 容器管理**:

```python
from appauto.manager.client_manager.linux import LinuxClient

# 创建客户端
client = LinuxClient(ip="192.168.1.100", user="admin", password="password")

# 获取 Docker 容器
containers = client.docker.ps()

# 在容器中执行命令
ft_container = client.docker_ctn_factory.ft
result = ft_container.exec("nvidia-smi")
```

#### 运行 pytest 测试

```python
from appauto.runners.pytest_runner import PytestRunner
from datetime import datetime

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

runner = PytestRunner(
    timestamp=timestamp,
    log_level="INFO",
    notify_group=None,
    notify_user=None,
    repeat=1,
    interval=0,
    no_report=False,
    testpaths="testcases/demo/"
)

return_code = runner.run()
```

#### 使用连接管理器

**HTTP 连接**:

```python
from appauto.manager.connection_manager.http import HttpClient

http = HttpClient(base_url="http://192.168.1.100:10011")
response = http.post("/v1/chat/completions", json={
    "model": "DeepSeek-R1",
    "messages": [{"role": "user", "content": "Hello"}]
})
```

**SSH 连接**:

```python
from appauto.manager.connection_manager.ssh import SSHClient

ssh = SSHClient(host="192.168.1.100", user="admin", password="password")
stdout, stderr, exit_code = ssh.exec_command("ls -la")
```

---

## 常见问题

### Q1: 如何更新版本号？

修改 `pyproject.toml` 中的 `version` 字段：

```toml
[project]
version = "0.1.2"  # 更新版本号
```

然后重新构建 wheel 包。

### Q2: 如何处理依赖冲突？

查看 `pyproject.toml` 中的 `dependencies` 列表，确保与目标环境兼容。可以通过 `pip install` 时添加 `--force-reinstall` 参数：

```bash
pip install --force-reinstall appauto-0.1.1-py3-none-any.whl
```

### Q3: 如何在虚拟环境中安装？

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装 wheel 包
pip install appauto-0.1.1-py3-none-any.whl
```

### Q4: 如何卸载？

```bash
pip uninstall appauto
```

### Q5: wheel 包文件名的含义？

`appauto-0.1.1-py3-none-any.whl` 各部分含义：

- `appauto`: 包名
- `0.1.1`: 版本号
- `py3`: 兼容 Python 3.x
- `none`: 无 ABI 标签（纯 Python 包）
- `any`: 支持任意平台

### Q6: 如何在离线环境安装？

1. 在有网络的环境下载依赖：

```bash
pip download appauto-0.1.1-py3-none-any.whl -d ./packages/
```

2. 将 `packages/` 目录复制到离线环境

3. 在离线环境安装：

```bash
pip install --no-index --find-links=./packages/ appauto-0.1.1-py3-none-any.whl
```

### Q7: 如何确认 CLI 入口点是否正确注册？

```bash
# 查看已安装的命令行工具
pip show -f appauto | grep "Location\|Files"

# 或直接运行
which appauto  # Linux/Mac
where appauto  # Windows
```

---

## 附录：完整构建流程示例

```bash
# 1. 清理旧的构建产物
rm -rf dist/ build/ *.egg-info .pdm-build/

# 2. 确保安装了构建工具
pip install --upgrade build pdm-backend

# 3. 运行构建
python -m build

# 4. 验证生成的文件
ls -lh dist/

# 5. (可选) 测试安装
pip install dist/appauto-0.1.1-py3-none-any.whl

# 6. 验证安装
appauto --version
python -c "import appauto; print(appauto.__version__)"

# 7. 上传到服务器（示例）
scp dist/appauto-0.1.1-py3-none-any.whl user@server:/mnt/data/packages/
```

---

## 技术支持

如有问题，请联系项目维护者：

- 作者: yanlong.wu
- 邮箱: yanlong.wu@approaching.ai
- 内部文档: http://192.168.110.11:8000/
- Jenkins 平台: http://192.168.110.11:9080/
