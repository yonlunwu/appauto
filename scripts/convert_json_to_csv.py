import json
import os
import csv
from glob import glob


def extract_json_to_csv(input_dir, output_csv):
    # 定义要提取的字段
    fields_to_extract = [
        "Average latency (s)",
        "Output token throughput (tok/s)",
        "Average time to first token (s)",
        "Average time per output token (s)",
    ]

    # CSV表头
    headers = ["Concurrency"] + fields_to_extract

    # 打开CSV文件准备写入
    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

        # 遍历所有benchmark_summary.json文件
        for json_file in glob(os.path.join(input_dir, "**", "benchmark_summary.json"), recursive=True):
            # 从路径中提取并发数
            dir_name = os.path.basename(os.path.dirname(json_file))
            if dir_name.startswith("parallel_"):
                concurrency = dir_name.split("_")[1]
            else:
                concurrency = "1"  # 默认值

            # 读取JSON文件
            with open(json_file, "r") as f:
                data = json.load(f)

            # 准备行数据
            row = [concurrency]
            for field in fields_to_extract:
                row.append(data.get(field, ""))

            # 写入CSV
            writer.writerow(row)


if __name__ == "__main__":
    # 使用示例
    input_directory = "outputs/20250709_135406/appauto-bench-5"
    output_csv_file = "benchmark_results.csv"
    extract_json_to_csv(
        input_dir=input_directory,
        output_csv=output_csv_file,
        input_length=512,  # 示例值，根据实际情况填写
        output_length=256,  # 示例值，根据实际情况填写
        loop=5,  # 示例值，根据实际情况填写
    )
