#!/bin/bash

# --- 变量定义 ---
REQUIRED_PYTHON_VERSION="3.10"
VENV_DIR="$HOME/perftest/venv/evalscope-py"
PYTHON_BIN="" # 存储找到的Python可执行文件路径

# 确保脚本在任何错误发生时退出
set -e

echo "=== 📜 环境配置脚本 (Ubuntu 22.04 LTS) 开始执行 ==="

# ----------------------------------------------------
# 步骤 1: 检查并添加当前用户免密 sudo 权限
# ----------------------------------------------------
echo "--- 检查免密 sudo 权限 ---"
CURRENT_USER=$(whoami)
SUDOERS_FILE="/etc/sudoers.d/${CURRENT_USER}_nopasswd"

if sudo -n true 2>/dev/null; then
    echo "✅ 当前用户 (${CURRENT_USER}) 已有免密 sudo 权限。"
else
    echo "⚠️ 当前用户 (${CURRENT_USER}) 缺少免密 sudo 权限，正在尝试添加..."

    # 检查是否已经存在该配置，防止重复添加
    if [ -f "$SUDOERS_FILE" ] && grep -q "${CURRENT_USER}" "$SUDOERS_FILE"; then
        echo "ℹ️ 配置似乎已存在于 ${SUDOERS_FILE}，但未生效。请检查 /etc/sudoers.d/ 权限和配置。"
    else
        # 使用 visudo -f 是一种更安全的写入方式，但需要交互式输入。
        # 这里使用 tee 和临时文件，并要求初始 sudo 权限
        TEMP_CONFIG="${CURRENT_USER} ALL=(ALL) NOPASSWD: ALL"
        
        # 使用 sudo tee 安全地创建和写入文件
        echo "$TEMP_CONFIG" | sudo tee "$SUDOERS_FILE" > /dev/null
        sudo chmod 0440 "$SUDOERS_FILE"
        echo "✅ 免密 sudo 权限已添加到 ${SUDOERS_FILE}。请验证是否生效。"
    fi
fi
# 此时不再测试，因为后续步骤需要它。

# ----------------------------------------------------
# 步骤 2: 检查 Python 版本 (>= 3.10)
# ----------------------------------------------------
echo "--- 检查 Python 版本 (要求 >= ${REQUIRED_PYTHON_VERSION}) ---"
PYTHON_COMMANDS=("python3.10" "python3" "python")
FOUND_PYTHON=false

for cmd in "${PYTHON_COMMANDS[@]}"; do
    if command -v "$cmd" &> /dev/null; then
        PYTHON_PATH=$(command -v "$cmd")
        # 提取主版本和次版本号进行比较
        VERSION_STRING=$("$PYTHON_PATH" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        
        # 使用 awk 或纯 bash 比较版本号
        # 将版本号转换为整数进行比较: 3.10 -> 310
        INT_VERSION=$(echo "$VERSION_STRING" | awk -F'.' '{printf "%d%02d", $1, $2}')
        REQUIRED_INT_VERSION=$(echo "$REQUIRED_PYTHON_VERSION" | awk -F'.' '{printf "%d%02d", $1, $2}')

        if [ "$INT_VERSION" -ge "$REQUIRED_INT_VERSION" ]; then
            PYTHON_BIN="$PYTHON_PATH"
            echo "✅ 找到满足条件的 Python：${PYTHON_BIN} (版本: ${VERSION_STRING})"
            FOUND_PYTHON=true
            break
        else
            echo "ℹ️ 找到 ${cmd}，但版本 (${VERSION_STRING}) 低于要求 (${REQUIRED_PYTHON_VERSION})。"
        fi
    fi
done

if ! $FOUND_PYTHON; then
    echo "❌ 未找到版本大于或等于 ${REQUIRED_PYTHON_VERSION} 的 Python 环境。"
    echo "请安装 Python ${REQUIRED_PYTHON_VERSION} 或更高版本后重新运行。"
    exit 1
fi

# ----------------------------------------------------
# 步骤 3: 检查并安装 virtualenv 命令
# ----------------------------------------------------
echo "--- 检查 virtualenv 命令 ---"
if command -v virtualenv &> /dev/null; then
    echo "✅ virtualenv 命令已安装。"
else
    echo "⚠️ virtualenv 命令未安装，正在安装..."
    # virtualenv 通常通过 pip 安装，如果系统中没有 pip，则需要先安装 python3-pip
    # 假设系统已经有找到的 Python 环境，我们使用其对应的 pip
    if ! command -v pip3 &> /dev/null; then
        echo "ℹ️ pip3 未找到，正在使用 apt 安装 python3-pip..."
        sudo apt update
        sudo apt install -y python3-pip
    fi

    # 安装 virtualenv
    pip3 install virtualenv
    echo "✅ virtualenv 安装完成。"
fi

# ----------------------------------------------------
# 步骤 4: 创建 venv 环境
# ----------------------------------------------------
echo "--- 创建 Python 虚拟环境: ${VENV_DIR} ---"
mkdir -p "$(dirname "$VENV_DIR")"
# 使用找到的 Python 路径来创建 venv
virtualenv -p "$PYTHON_BIN" "$VENV_DIR"
echo "✅ 虚拟环境创建成功。"

# ----------------------------------------------------
# 步骤 5: 激活 venv 并安装依赖
# ----------------------------------------------------
echo "--- 激活 venv 并安装依赖 ---"
# 激活环境
source "$VENV_DIR/bin/activate"

# 检查激活状态 (可选)
if [[ "$VIRTUAL_ENV" == "$VENV_DIR" ]]; then
    echo "✅ 虚拟环境已成功激活。"
else
    echo "❌ 虚拟环境激活失败，继续尝试使用全路径安装。"
    # 如果 source 失败，我们仍然可以使用全路径的 pip
    PIP_BIN="$VENV_DIR/bin/pip"
    
    if [ ! -f "$PIP_BIN" ]; then
        echo "致命错误: 在 ${VENV_DIR}/bin/ 中未找到 pip 可执行文件。"
        exit 1
    fi
fi

# 设置 PIP_BIN 变量，确保使用 venv 中的 pip
PIP_BIN="${VENV_DIR}/bin/pip"

echo "➡️ 开始安装依赖 (使用清华镜像源): evalscope==1.0.1, uvicorn, fastapi, sse_starlette, openpyxl, jinja2"
"$PIP_BIN" install \
    evalscope==1.0.1 \
    uvicorn \
    fastapi \
    sse_starlette \
    openpyxl \
    jinja2 \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

echo "✅ 所有依赖安装完成。"

# ----------------------------------------------------
# 步骤 6: 测试 evalscope 环境和版本
# ----------------------------------------------------
echo "--- 测试 evalscope 环境和版本 ---"
# 使用 venv 中的 evalscope 可执行文件
EVALSCOPE_BIN="$VENV_DIR/bin/evalscope"

if [ -f "$EVALSCOPE_BIN" ]; then
    VERSION_OUTPUT=$("$EVALSCOPE_BIN" --version 2>&1)
    
    if echo "$VERSION_OUTPUT" | grep -q "1.0.1"; then
        echo "✅ evalscope 环境测试通过。版本为 1.0.1。"
    else
        echo "❌ evalscope 版本检查失败。预期版本 1.0.1，实际输出："
        echo "$VERSION_OUTPUT"
        deactivate 2>/dev/null || true
        exit 1
    fi
else
    echo "❌ 在 ${VENV_DIR}/bin/ 中未找到 evalscope 可执行文件。"
    deactivate 2>/dev/null || true
    exit 1
fi

# 退出 venv
deactivate 2>/dev/null || true
echo "--- 脚本执行完毕。环境配置成功！ ---"
echo "--- 您可以通过以下命令激活环境：source ${VENV_DIR}/bin/activate ---"
echo "==========================================================="

# 退出，表示成功
exit 0
