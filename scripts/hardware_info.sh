      
#!/bin/bash

# 硬件信息收集脚本
# 收集 CPU、内存和 NVIDIA 显卡信息

OUTPUT_FILE="hardware_info_$(date +%Y%m%d_%H%M%S).txt"

echo "========================================" > "$OUTPUT_FILE"
echo "硬件信息收集报告" >> "$OUTPUT_FILE"
echo "收集时间: $(date)" >> "$OUTPUT_FILE"
echo "主机名: $(hostname)" >> "$OUTPUT_FILE"
echo "========================================" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 网络信息
echo "=== 网络信息 ===" >> "$OUTPUT_FILE"
echo "内网 IP:" >> "$OUTPUT_FILE"
ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}/\d+' | grep -v '127.0.0.1' | while read ip; do
    echo "  $ip" >> "$OUTPUT_FILE"
done
echo "外网 IP: $(curl -s ifconfig.me 2>/dev/null || echo "无法获取")" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# CPU 信息
echo "=== CPU 信息 ===" >> "$OUTPUT_FILE"
echo "型号: $(lscpu | grep "Model name" | sed 's/Model name:[ ]*//')" >> "$OUTPUT_FILE"
echo "架构: $(lscpu | grep "Architecture" | sed 's/Architecture:[ ]*//')" >> "$OUTPUT_FILE"
echo "CPU 数量: $(lscpu | grep "^CPU(s):" | sed 's/CPU(s):[ ]*//')" >> "$OUTPUT_FILE"
echo "每个 CPU 核心数: $(lscpu | grep "Core(s) per socket" | sed 's/Core(s) per socket:[ ]*//')" >> "$OUTPUT_FILE"
echo "线程数每核: $(lscpu | grep "Thread(s) per core" | sed 's/Thread(s) per core:[ ]*//')" >> "$OUTPUT_FILE"
echo "CPU 频率: $(lscpu | grep "CPU MHz" | sed 's/CPU MHz:[ ]*//')MHz" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# 内存信息
echo "=== 内存信息 ===" >> "$OUTPUT_FILE"
echo "总内存: $(free -h | grep "^Mem:" | awk '{print $2}')" >> "$OUTPUT_FILE"
echo "交换空间: $(free -h | grep "^Swap:" | awk '{print $2}')" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# NVIDIA 显卡信息
echo "=== NVIDIA 显卡信息 ===" >> "$OUTPUT_FILE"
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader | while IFS=',' read -r name mem driver; do
        echo "显卡型号: $name" >> "$OUTPUT_FILE"
        echo "显存大小: $mem" >> "$OUTPUT_FILE"
        echo "驱动版本: $driver" >> "$OUTPUT_FILE"
    done
    echo "CUDA 版本: $(nvidia-smi | grep -Po 'CUDA Version: \K[0-9.]+')" >> "$OUTPUT_FILE"
else
    echo "未检测到 NVIDIA 显卡或驱动" >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

# 华为昇腾 NPU 信息
echo "=== 华为昇腾 NPU 信息 ===" >> "$OUTPUT_FILE"
if command -v npu-smi &> /dev/null; then
    # 检测是否需要 sudo 权限
    if npu-smi info -m 2>&1 | grep -q "dcmi module initialize failed"; then
        NPU_CMD="sudo npu-smi"
    else
        NPU_CMD="npu-smi"
    fi

    # 获取 NPU 设备列表，过滤出 Ascend 芯片（排除 Mcu 行）
    npu_list=$($NPU_CMD info -m 2>/dev/null | grep "Ascend")
    npu_count=$(echo "$npu_list" | wc -l)

    if [ "$npu_count" -gt 0 ]; then
        echo "检测到 $npu_count 个 NPU 设备" >> "$OUTPUT_FILE"

        # 从列表中提取唯一的 NPU ID
        npu_ids=$(echo "$npu_list" | awk '{print $1}' | sort -u)

        # 遍历每个 NPU ID
        for npu_id in $npu_ids; do
            echo "" >> "$OUTPUT_FILE"

            # 从列表中获取芯片型号
            chip_name=$(echo "$npu_list" | grep "^[[:space:]]*$npu_id[[:space:]]" | awk '{print $NF}' | head -1)
            echo "NPU $npu_id: $chip_name" >> "$OUTPUT_FILE"

            # 获取板卡信息
            board_info=$($NPU_CMD info -t board -i $npu_id 2>/dev/null)
            product_name=$(echo "$board_info" | grep "Product Name" | awk -F':' '{print $2}' | xargs)
            if [ -n "$product_name" ]; then
                echo "  产品名称: $product_name" >> "$OUTPUT_FILE"
            fi

            firmware_ver=$(echo "$board_info" | grep "Firmware Version" | awk -F':' '{print $2}' | xargs)
            if [ -n "$firmware_ver" ]; then
                echo "  固件版本: $firmware_ver" >> "$OUTPUT_FILE"
            fi

            # 获取内存信息
            mem_info=$($NPU_CMD info -t memory -i $npu_id 2>/dev/null)
            hbm_cap=$(echo "$mem_info" | grep "HBM Capacity" | awk -F':' '{print $2}' | xargs)
            if [ -n "$hbm_cap" ]; then
                echo "  HBM 内存: $hbm_cap" >> "$OUTPUT_FILE"
            fi
        done
    else
        echo "未检测到可用的 NPU 设备（可能需要 sudo 权限）" >> "$OUTPUT_FILE"
    fi
else
    echo "未检测到华为昇腾 NPU 或驱动" >> "$OUTPUT_FILE"
fi
echo "" >> "$OUTPUT_FILE"

echo "========================================" >> "$OUTPUT_FILE"
echo "收集完成！" >> "$OUTPUT_FILE"
echo "========================================" >> "$OUTPUT_FILE"

echo "硬件信息已保存到: $OUTPUT_FILE"
