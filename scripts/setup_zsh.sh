#!/bin/bash

# --- 预设目录 ---
ZSH_CUSTOM_DIR="$HOME/.oh-my-zsh/custom"
ZSHRC_FILE="$HOME/.zshrc"

echo "### Zsh 环境设置脚本 (已包含 zsh-autosuggestions 和 zsh-syntax-highlighting) ###"

# 1. 检查/安装 Zsh
if ! command -v zsh &> /dev/null; then
    echo "Zsh 未安装。正在尝试安装 Zsh..."
    if sudo apt update && sudo apt install -y zsh; then
        echo "Zsh 安装成功。"
    else
        echo "错误：Zsh 安装失败。请检查您的权限或网络连接。"
        exit 1
    fi
else
    echo "Zsh 已安装。"
fi

# 2. 检查/安装 Oh My Zsh
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    echo "正在安装 Oh My Zsh..."
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
    if [ $? -ne 0 ]; then
        echo "错误：Oh My Zsh 安装失败。"
        exit 1
    fi
else
    echo "Oh My Zsh 已安装。"
fi

# 3. 安装 zsh-autosuggestions 插件
echo "正在安装 zsh-autosuggestions 插件..."
AUTOSUGGESTIONS_DIR="$ZSH_CUSTOM_DIR/plugins/zsh-autosuggestions"
if [ ! -d "$AUTOSUGGESTIONS_DIR" ]; then
    git clone https://github.com/zsh-users/zsh-autosuggestions "$AUTOSUGGESTIONS_DIR"
    if [ $? -ne 0 ]; then
        echo "错误：zsh-autosuggestions 插件安装失败。"
    fi
else
    echo "zsh-autosuggestions 插件已存在。"
fi

# 4. 安装 zsh-syntax-highlighting 插件
echo "正在安装 zsh-syntax-highlighting 插件..."
SYNTAX_HIGHLIGHTING_DIR="$ZSH_CUSTOM_DIR/plugins/zsh-syntax-highlighting"
if [ ! -d "$SYNTAX_HIGHLIGHTING_DIR" ]; then
    git clone https://github.com/zsh-users/zsh-syntax-highlighting.git "$SYNTAX_HIGHLIGHTING_DIR"
    if [ $? -ne 0 ]; then
        echo "错误：zsh-syntax-highlighting 插件安装失败。"
    fi
else
    echo "zsh-syntax-highlighting 插件已存在。"
fi

# 5. 配置 .zshrc 文件
echo "正在配置 $ZSHRC_FILE 文件..."

# A. 设置主题为 "maran"
sed -i '/^ZSH_THEME=/c\ZSH_THEME="maran"' "$ZSHRC_FILE"

# B. 启用插件 (确保包含 git, zsh-autosuggestions, zsh-syntax-highlighting)
PLUGINS="git zsh-autosuggestions zsh-syntax-highlighting"

# 检查 plugins 行是否存在并替换
if grep -q '^plugins=' "$ZSHRC_FILE"; then
    # 使用 awk 来替换 plugins=(...) 这一整行，确保格式正确
    awk -v plugins="$PLUGINS" '/^plugins=/ {print "plugins=(" plugins ")" ; next} 1' "$ZSHRC_FILE" > "$ZSHRC_FILE.tmp" && mv "$ZSHRC_FILE.tmp" "$ZSHRC_FILE"
else
    # 如果 plugins 行不存在，则添加它
    echo "plugins=($PLUGINS)" >> "$ZSHRC_FILE"
fi

# 6. 更改用户的默认 shell
echo "正在尝试将默认 shell 更改为 Zsh (需要密码)..."
chsh -s "$(which zsh)"

if [ $? -eq 0 ]; then
    echo "默认 shell 已成功更改为 $(which zsh)。"
    echo "请 **退出当前终端会话** 并 **重新登录** 或 **打开一个新的终端窗口** 以使用 Zsh。"
    echo "新 Zsh 的主题为 'maran'，并已启用所有指定插件。"
else
    echo "警告：无法自动更改默认 shell。请手动运行以下命令："
    echo "chsh -s $(which zsh)"
fi

exit 0
