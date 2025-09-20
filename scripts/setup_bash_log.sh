#!/bin/bash

# 功能：配置全局 bash 命令日志记录，记录所有用户的操作历史到 /var/log/bash.log
# 包含时间、用户、IP、终端、退出状态码等信息，并配置日志轮转

# 检查是否以root权限运行
if [ "$(id -u)" -ne 0 ]; then
    echo "错误：此脚本需要root权限运行，请使用sudo执行" >&2
    exit 1
fi

# 创建日志文件并设置权限
echo "创建日志文件并设置权限..."
touch /var/log/bash.log
chmod 644 /var/log/bash.log
chown root:root /var/log/bash.log

# 确认当前shell是否为bash
echo "检查当前默认shell..."
if [ "$SHELL" != "/bin/bash" ]; then
    echo "警告：当前默认shell不是bash，本脚本可能无法正常工作" >&2
fi

# 配置全局bash日志钩子（/etc/bash.bashrc）
echo "配置全局bash日志记录..."
bashrc_path="/etc/bash.bashrc"

# 检查函数是否已存在，避免重复添加
if ! grep -q "record_global_command()" "$bashrc_path"; then
    cat << 'EOF' >> "$bashrc_path"

record_global_command() {

    local exit_code=$?

    local hist_line=$(history 1)
    local hist_num=$(echo "$hist_line" | awk '{print $1}')
    local last_cmd=$(echo "$hist_line" | sed "s/^[ ]*$hist_num[ ]*//")  # 提取命令内容

    # 空命令不记录
    [ -z "$last_cmd" ] && return

    if [ "$hist_num" = "$LAST_HIST_NUM" ]; then
        return  # 编号相同，说明是重复触发，跳过
    fi
    export LAST_HIST_NUM="$hist_num"  # 更新为最新编号

    # 收集日志信息
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    local user=$(whoami)
    local tty=$(tty | sed 's/\/dev\///')
    local ip=$(echo $SSH_CONNECTION | awk '{print $1}')
    [ -z "$ip" ] && ip="local"

    # 写入日志（仅root可写，避免篡改）
    echo "[$timestamp] [USER:$user] [IP:$ip] [TTY:$tty] [EXIT:$exit_code] [HIST:$hist_num] $last_cmd" | sudo tee -a /var/log/bash.log > /dev/null 2>&1
}

# 确保PROMPT_COMMAND中只添加一次函数（防重复）
if ! echo "$PROMPT_COMMAND" | grep -q "record_global_command"; then
    # 保留原有PROMPT_COMMAND内容，仅追加新函数
    export PROMPT_COMMAND="record_global_command; $PROMPT_COMMAND"
fi
EOF
else
    echo "全局日志记录函数已存在，跳过添加"
fi

# 配置日志轮转
echo "配置日志轮转..."
logrotate_conf="/etc/logrotate.d/bashlog"

if [ ! -f "$logrotate_conf" ]; then
    cat << 'EOF' > "$logrotate_conf"
/var/log/bash.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
    create 644 root root
}
EOF
else
    echo "日志轮转配置已存在，跳过创建"
fi

echo "配置完成！新的bash会话将开始记录命令日志到/var/log/bash.log"
echo "提示：已有的bash会话需要重新登录才能生效"
