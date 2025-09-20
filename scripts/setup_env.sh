#!/bin/bash
set -x

# 设置变量
PROJECT_DIR="$HOME/perftest"
VENV_NAME="evalscope-py"
VENV_PATH="$PROJECT_DIR/venv/$VENV_NAME"
PYTHON_BIN="$(command -v python3.10 || command -v python3 || command -v python)"
PYTHON_VENV="$VENV_PATH/bin/python"

# 检查 PYTHON_BIN 是否有效
if [[ -z "$PYTHON_BIN" ]]; then
  echo "ERROR: No Python executable provided or found in PATH." >&2
  exit 1
fi

echo "Using Python from: $PYTHON_BIN"

# 检查 virtualenv 是否存在
if ! command -v virtualenv &>/dev/null; then
  echo "virtualenv not found."

  # 尝试安装 virtualenv
  echo "Installing virtualenv via pip..."
  "$PYTHON_BIN" -m pip install virtualenv -i https://pypi.tuna.tsinghua.edu.cn/simple

  # 再次检查是否安装成功
  if ! command -v virtualenv &>/dev/null; then
    echo "ERROR: Failed to install virtualenv." >&2
    echo "Please check your pip and Python environment." >&2
    exit 1
  else
    echo "virtualenv installed successfully."
  fi
else
  echo "virtualenv is already available."
fi

# 创建虚拟环境目录（如果不存在）
mkdir -p "$PROJECT_DIR/venv"

# 创建虚拟环境
echo "Creating virtual environment..."
virtualenv -p "$PYTHON_BIN" "$VENV_PATH"

# 激活虚拟环境
echo "Activating virtual environment..."
source "$VENV_PATH/bin/activate"


# 打印当前环境信息
echo ""
echo "✅ Successfully activated virtual environment:"
echo "Python: $(which python)"
echo "Pip: $(which pip)"
echo ""

# 升级 pip（可选）
$PYTHON_VENV -m pip install --upgrade pip

# 安装 evalscope 及其所有依赖
echo "Installing evalscope and dependencies..."
$PYTHON_VENV -m pip install evalscope==0.17.0 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 显示安装结果
echo "Installation completed. Installed packages:"
pip list

# 提示用户如何激活环境
echo ""
echo "✅ Setup completed successfully!"
echo "To activate the virtual environment in the future, run:"
echo "source $VENV_PATH/bin/activate"
echo "Show evalscope location, run:"
echo "which evalscope"