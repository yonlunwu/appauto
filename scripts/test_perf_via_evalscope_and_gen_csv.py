"""
通过 evalscope 跑 perf 测试并生成 csv.
"""

import os
import csv
import json
import click
from glob import glob
from uuid import uuid4
from datetime import datetime

from evalscope.perf.main import run_perf_benchmark
from evalscope.perf.arguments import Arguments


def extract_json_to_csv(input_dir, output_csv, input_length, output_length, loop):
    # 定义要提取的字段
    fields_to_extract = [
        "Average latency (s)",
        "Output token throughput (tok/s)",
        "Average time to first token (s)",
        "Average time per output token (s)",
    ]

    # CSV表头 - 新增的三个参数在前三列
    headers = ["Input Length", "Output Length", "Loop", "Concurrency"] + fields_to_extract

    # 检查文件是否存在以决定写入模式
    file_exists = os.path.isfile(output_csv)

    # 收集当前loop的所有行数据
    all_rows = []

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
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"警告: 无法解析JSON文件: {json_file}")
                continue

        # 准备行数据 - 新增的三个参数在前三列
        row = [input_length, output_length, loop, int(concurrency)]  # 将并发数转为整数以便排序
        for field in fields_to_extract:
            row.append(data.get(field, ""))

        all_rows.append(row)

    # 按并发数从小到大排序
    all_rows.sort(key=lambda x: x[3])  # 索引3是并发数列

    # 打开CSV文件准备写入
    with open(output_csv, "a" if file_exists else "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # 只在文件不存在时写入表头
        if not file_exists:
            writer.writerow(headers)

        # 写入排序后的所有行
        writer.writerows(all_rows)


@click.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True, help_option_names=["-h", "--help"])
)
@click.option("--ip", required=True, help="AMaaS management IP")
@click.option("--port", type=str, default=10011, show_default=True, help="AMaaS management IP")
@click.option("--parallel", type=str, default="1 4", show_default=True, help="并发数, 请用引号引起来, 如 '1 4'")
@click.option("--number", type=str, default="1 4", show_default=True, help="请求数, 请用引号引起来, 如 '1 4'")
@click.option("--model", type=str, default="DeepSeek-R1", show_default=True, help="模型名称")
@click.option("--tokenizer-path", type=str, default="/mnt/data/models/DeepSeek-R1-GPTQ4-experts", show_default=True)
@click.option(
    "--api-key", type=str, default="AMES_07af0a0dc8d52ea0_d84228a38540674a90b2b70434823e2e", show_default=True
)
@click.option("--input-length", type=int, default=128, show_default=True)
@click.option("--output-length", type=int, default=256, show_default=True)
@click.option("--seed", type=int, default=42, show_default=True)
@click.option("--loop", type=int, default=1, show_default=True)
@click.option("--name", type=str, default="appauto-bench", show_default=True, help="任务名称")
@click.option("--debug", is_flag=True, show_default=True)
@click.option("--output-csv", type=str, default=None, show_default=True, help="输出 csv 文件名称, 不填写会默认填充")
def runner(
    ip,
    port,
    parallel,
    number,
    model,
    api_key,
    input_length,
    output_length,
    tokenizer_path,
    seed,
    loop,
    name,
    debug,
    output_csv,
):
    start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_csv = (
        f"{output_csv}_{start_time}.csv" if output_csv else f"{start_time}.csv" or f"{start_time}_{str(uuid4)}.csv"
    )

    number = [int(n) for n in number.split()]
    parallel = [int(p) for p in parallel.split()]

    for i in range(0, int(loop)):
        print(f" loop {i} ".center(100, "*"))

        task_cfg = Arguments(
            parallel=parallel,
            number=number,
            model=model,
            url=f"http://{ip}:{int(port)}/v1/chat/completions",
            api_key=api_key,
            api="openai",
            dataset="random",
            min_tokens=int(output_length),
            max_tokens=int(output_length),
            prefix_length=0,
            min_prompt_length=int(input_length),
            max_prompt_length=int(input_length),
            tokenizer_path=tokenizer_path,
            extra_args={"ignore_eos": True},
            # swanlab_api_key="local",
            seed=int(seed),
            name=f"{name}-{i}",
            debug=debug,
        )

        # len(number) != 1: ./outputs/20250709_142517/{name}/parallel_x_number_x/benchmark_summary.json
        # len(number) == 1: ./outputs/20250708_232819/{name}/benchmark_summary.json
        run_perf_benchmark(task_cfg)

        # 从 json 提取至 csv
        if len(number) == 1:
            # 读 json TODO 如何感知 timestamp? -> args.outputs_dir 可以感知到
            json_dir = task_cfg.outputs_dir  # 已经包括了 name
            extract_json_to_csv(json_dir, output_csv, input_length, output_length, i)

        elif len(number) > 1:
            json_dir = "/".join(task_cfg.outputs_dir.split("/")[:-2])
            extract_json_to_csv(json_dir, output_csv, input_length, output_length, i)

    print(f"Save the csv result to: {output_csv}")


if __name__ == "__main__":
    runner(obj={})
