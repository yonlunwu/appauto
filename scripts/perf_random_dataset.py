"""
通过 evalscope 跑 perf 测试并生成 csv & xlsx.
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


def extract_json_to_csv(input_dir, output_csv, input_length, output_length, loop, concurrency: int = None):
    # 定义要提取的字段
    fields_to_extract = [
        "Average latency (s)",
        "Output token throughput (tok/s)",
        "Average time to first token (s)",
        "Average time per output token (s)",
    ]

    # CSV 表头
    headers = ["Input Length", "Output Length", "Loop", "Concurrency"] + fields_to_extract

    # 检查文件是否存在以决定写入模式
    file_exists = os.path.isfile(output_csv)

    # 收集当前 loop 的所有行数据
    all_rows = []

    # 遍历 benchmark_summary.json
    for json_file in glob(os.path.join(input_dir, "**", "benchmark_summary.json"), recursive=True):
        # 从路径中提取并发数
        dir_name = os.path.basename(os.path.dirname(json_file))
        if dir_name.startswith("parallel_"):
            concurrency = dir_name.split("_")[1]
        else:
            concurrency = concurrency or "1"  # 默认值

        with open(json_file, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"警告: 无法解析JSON文件: {json_file}")
                continue

        # 准备行数据
        row = [input_length, output_length, loop, int(concurrency)]  # 将并发数转为整数以便排序
        for field in fields_to_extract:
            row.append(data.get(field, ""))

        all_rows.append(row)

    # 按并发数从小到大排序
    all_rows.sort(key=lambda x: x[3])  # 索引 3 是并发数列

    # 处理 csv
    with open(output_csv, "a" if file_exists else "w", newline="") as csvfile:
        writer = csv.writer(csvfile)

        # 只在文件不存在时写入表头
        if not file_exists:
            writer.writerow(headers)

        # 写入排序后的所有行
        writer.writerows(all_rows)


def parse_csv_to_xlsx(in_csv, out_xlsx):
    import pandas as pd
    from openpyxl import Workbook
    from openpyxl.utils.dataframe import dataframe_to_rows

    # 1. 读数据
    df = pd.read_csv(in_csv)

    # 2. 计算每一轮的 Avg TPS 和 Avg throughput
    df["单轮次 Avg TPS"] = 1 / df["Average time per output token (s)"]
    df["单轮次平均单路吞吐（tok/s）"] = df["Output token throughput (tok/s)"] / df["Concurrency"]

    # 3. 计算相同工况所有轮次的 Avg TPS 和 Avg throughput
    avg_tps_all_round = (
        df.groupby(["Input Length", "Output Length", "Concurrency"])["单轮次 Avg TPS"]
        .mean()
        .rename("所有轮次平均 TPS")
        .reset_index()
    )

    df = df.merge(avg_tps_all_round, on=["Input Length", "Output Length", "Concurrency"], how="left")

    avg_tp_all_round = (
        df.groupby(["Input Length", "Output Length", "Concurrency"])["单轮次平均单路吞吐（tok/s）"]
        .mean()
        .rename("所有轮次平均单路吞吐（tok/s）")
        .reset_index()
    )
    df = df.merge(avg_tp_all_round, on=["Input Length", "Output Length", "Concurrency"], how="left")

    # 4. 写 Excel
    wb = Workbook()
    ws = wb.active
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)

    ws.cell(row=1, column=df.columns.get_loc("所有轮次平均单路吞吐（tok/s）") + 1).column_letter

    wb.save(out_xlsx)
    print("Save the xlsx result to: ", out_xlsx)


@click.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True, help_option_names=["-h", "--help"])
)
@click.option("--ip", required=True, help="AMaaS 管理 IP")
@click.option("--port", type=str, default=10011, show_default=True)
@click.option("--parallel", type=str, default="1 4", show_default=True, help="并发数, 请用引号引起来, 如 '1 4'")
@click.option("--number", type=str, default="1 4", show_default=True, help="请求数, 请用引号引起来, 如 '1 4'")
@click.option("--model", type=str, default="DeepSeek-R1", show_default=True, help="模型名称")
@click.option("--tokenizer-path", type=str, default="/mnt/data/models/DeepSeek-R1-GPTQ4-experts", show_default=True)
@click.option(
    "--api-key",
    type=str,
    default="AMES_89c2bb9cfba90d8b_5d7e9cc1d9f412b038bd11d7b559fd47",
    show_default=True,
    help="API Key, 从 AMaaS 上创建.",
)
@click.option("--input-length", type=int, default=128, show_default=True)
@click.option("--output-length", type=int, default=512, show_default=True)
@click.option("--read-timeout", type=int, default=600, show_default=True)
@click.option("--seed", type=int, default=42, show_default=True)
@click.option("--loop", type=int, default=1, show_default=True)
@click.option("--name", type=str, default="appauto-bench", show_default=True, help="任务名称")
@click.option("--debug", is_flag=True, show_default=True)
@click.option("--output-csv", type=str, default=None, show_default=True, help="输出 csv 文件名称, 不填写会默认填充")
@click.option("--output-xlsx", type=str, default=None, show_default=True, help="同时输出一份 xlsx 文件")
def runner(
    ip,
    port,
    parallel,
    number,
    model,
    api_key,
    input_length,
    output_length,
    read_timeout,
    tokenizer_path,
    seed,
    loop,
    name,
    debug,
    output_csv,
    output_xlsx,
):
    start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_csv = (
        f"{output_csv}_{start_time}.csv" if output_csv else f"{start_time}.csv" or f"{start_time}_{str(uuid4)}.csv"
    )
    output_xlsx = output_csv.replace(".csv", ".xlsx")

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
            read_timeout=int(read_timeout),
            prefix_length=0,
            min_prompt_length=int(input_length),
            max_prompt_length=int(input_length),
            tokenizer_path=tokenizer_path,
            extra_args={"ignore_eos": True},
            # swanlab_api_key="local",
            seed=int(seed),
            name=f"{name}-{i}",
            debug=debug,
            stream=True
        )

        # len(number) != 1: ./outputs/20250709_142517/{name}/parallel_x_number_x/benchmark_summary.json
        # len(number) == 1: ./outputs/20250708_232819/{name}/benchmark_summary.json
        run_perf_benchmark(task_cfg)

        # 从 json 提取至 csv
        if len(number) == 1:
            # 读 json TODO 如何感知 timestamp? -> args.outputs_dir 可以感知到
            json_dir = task_cfg.outputs_dir  # 已经包括了 name

        elif len(number) > 1:
            json_dir = "/".join(task_cfg.outputs_dir.split("/")[:-2])

        extract_json_to_csv(
            json_dir, output_csv, input_length, output_length, i, None if len(parallel) > 1 else parallel[0]
        )

    print(f"Save the csv result to: {output_csv}")

    parse_csv_to_xlsx(output_csv, output_xlsx)


if __name__ == "__main__":
    runner(obj={})
