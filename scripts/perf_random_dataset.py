"""
通过 evalscope 跑 perf 测试并生成 csv & xlsx.
"""

import os
import csv
import json
import click
import httpx
import pandas as pd
from glob import glob
from random import randint
from datetime import datetime
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from evalscope.perf.arguments import Arguments
from evalscope.perf.main import run_perf_benchmark


def extract_json_to_csv(input_dir, output_csv, input_length, output_length, loop, concurrency: int = None):
    # 初始化空列表存储所有JSON字段和临时行数据
    exclude_fields = ["Number of concurrency"]
    all_json_fields = []
    temp_rows = []  # 替代原来的 all_rows，先存所有行再处理表头
    # 检查文件是否存在以决定写入模式
    file_exists = os.path.isfile(output_csv)
    # 第一步：先遍历所有JSON文件，收集所有需要的字段（排除指定字段）
    for json_file in glob(os.path.join(input_dir, "**", "benchmark_summary.json"), recursive=True):
        with open(json_file, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"警告: 无法解析JSON文件: {json_file}")
                continue
        # 动态收集字段：排除指定字段，去重
        for field in data.keys():
            if field not in exclude_fields and field not in all_json_fields:
                all_json_fields.append(field)
        # 组装行数据（基础参数 + 所有JSON字段值）
        row_base = [input_length, output_length, loop, int(concurrency)]  # 基础参数
        row_json = [data.get(field, "") for field in all_json_fields]  # 所有JSON字段的值
        full_row = row_base + row_json  # 合并成完整行
        temp_rows.append(full_row)  # 用 temp_rows 替代原来的 all_rows
    # 生成动态表头（基础列 + 所有JSON字段列）
    headers = ["Input Length", "Output Length", "Loop", "Concurrency"] + all_json_fields
    # 按并发数排序（把 all_rows 换成 temp_rows）
    temp_rows.sort(key=lambda x: x[3])  # 索引 3 是并发数列
    # 处理 csv
    with open(output_csv, "a" if file_exists else "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # 只在文件不存在时写入表头
        if not file_exists:
            writer.writerow(headers)
        # 写入排序后的所有行
        writer.writerows(temp_rows)


def parse_csv_to_xlsx(in_csv, out_xlsx):
    # 1. 读数据
    df = pd.read_csv(in_csv)
    # 2. 计算每一轮的 Avg TPS 和 Avg throughput
    # 增加字段存在性检查 + 防除0错误
    # 计算每一轮的 Avg TPS 和 Avg throughput（容错版）
    if "Average time per output token (s)" in df.columns:
        # 替换0值为NaN，避免除以0报错
        df["单轮次 Avg TPS"] = 1 / df["Average time per output token (s)"].replace(0, pd.NA)
    else:
        df["单轮次 Avg TPS"] = pd.NA
        print("警告：没找到 'Average time per output token (s)' 字段，无法计算TPS")
    if "Output token throughput (tok/s)" in df.columns and "Concurrency" in df.columns:
        df["单轮次平均单路吞吐（tok/s）"] = df["Output token throughput (tok/s)"] / df["Concurrency"]
    else:
        df["单轮次平均单路吞吐（tok/s）"] = pd.NA
        print("警告：缺少字段，无法计算单路吞吐")
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
    # 4. 动态拼接字段顺序（核心：不写死，自动适配）
    # 基础字段（固定）
    base_cols = ["Input Length", "Output Length", "Loop", "Concurrency"]
    # 动态获取JSON字段（排除基础字段和TPS字段）
    json_cols = [
        col
        for col in df.columns
        if col not in base_cols
        and col
        not in ["单轮次 Avg TPS", "单轮次平均单路吞吐（tok/s）", "所有轮次平均 TPS", "所有轮次平均单路吞吐（tok/s）"]
    ]
    # TPS计算字段（固定）
    tps_cols = ["单轮次 Avg TPS", "单轮次平均单路吞吐（tok/s）", "所有轮次平均 TPS", "所有轮次平均单路吞吐（tok/s）"]
    # 拼接最终字段顺序：基础字段 + JSON字段 + TPS字段
    custom_columns = base_cols + json_cols + tps_cols
    # 只保留自定义的字段（过滤掉不需要的字段）
    df = df[custom_columns]
    # 5. 写 Excel
    wb = Workbook()
    ws = wb.active
    for r in dataframe_to_rows(df, index=False, header=True):
        ws.append(r)
    ws.cell(row=1, column=df.columns.get_loc("所有轮次平均单路吞吐（tok/s）") + 1).column_letter
    df.to_csv(out_xlsx.replace(".xlsx", ".csv"), index=False)
    wb.save(out_xlsx)
    print("Save the xlsx result to: ", out_xlsx)


@click.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True, help_option_names=["-h", "--help"])
)
@click.option("--ip", type=str, default="127.0.0.1", show_default=True, help="AMaaS 管理 IP")
@click.option("--port", type=str, default=10011, show_default=True, help="AMaaS API 端口")
@click.option("--rate", type=int, default=None, show_default=True)
@click.option("--parallel", type=str, default="1 4", show_default=True, help="并发数, 请用引号引起来, 如 '1 4'")
@click.option("--number", type=str, default="1 4", show_default=True, help="请求数, 请用引号引起来, 如 '1 4'")
@click.option("--model", type=str, default="/mnt/shared/models/DeepSeek-R1-0528", show_default=True, help="模型名称")
@click.option("--tokenizer-path", type=str, default="/mnt/shared/models/DeepSeek-R1-0528", show_default=True)
@click.option(
    "--api-key",
    type=str,
    default="AMES_89c2bb9cfba90d8b_5d7e9cc1d9f412b038bd11d7b559fd47",
    show_default=True,
    help="API Key, 从 AMaaS 上创建.",
)
@click.option("--input-length", type=int, default=128, show_default=True)
@click.option("--output-length", type=int, default=512, show_default=True)
@click.option("--read-timeout", type=int, default=3600, show_default=True)
@click.option("--loop", type=int, default=1, show_default=True)
@click.option("--name", type=str, default="appauto-bench", show_default=True, help="任务名称")
@click.option("--debug", is_flag=True, show_default=True)
@click.option("--use-chat", is_flag=True, show_default=True)
@click.option("--output-csv", type=str, default=None, show_default=True, help="输出 csv 文件名称, 不填写会默认填充")
@click.option("--output-xlsx", type=str, default=None, show_default=True, help="同时输出一份 xlsx 文件")
def runner(
    ip,
    port,
    rate,
    parallel,
    number,
    model,
    api_key,
    input_length,
    output_length,
    read_timeout,
    tokenizer_path,
    loop,
    name,
    debug,
    use_chat,
    output_csv,
    output_xlsx,
):
    start_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_csv = f"{output_csv}.csv" if output_csv else f"{start_time}.csv"
    output_xlsx = output_csv.replace(".csv", ".xlsx")
    number_list = [int(n) for n in number.split()]
    parallel_list = [int(p) for p in parallel.split()]
    url = f"http://{ip}:{int(port)}/v1/completions" if not use_chat else f"http://{ip}:{int(port)}/v1/chat/completions"
    for i in range(0, int(loop)):
        print(f" loop {i} ".center(100, "*"))
        for p, n in zip(parallel_list, number_list):
            print(f" Running parallel: {p}, number: {n} ".center(80, "-"))
            task_cfg = Arguments(
                parallel=[p],
                number=[n],
                model=model,
                url=url,
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
                seed=randint(0, 200),
                name=f"{name}-{i}-p{p}",
                debug=debug,
                stream=True,
            )
            if rate:
                task_cfg.rate = int(rate)
            # 执行压测
            run_perf_benchmark(task_cfg)
            # 从 json 提取至 csv
            # 因为每次只跑一组 (p, n)，evalscope 会直接在 task_cfg.outputs_dir 下生成 json
            json_dir = task_cfg.outputs_dir
            extract_json_to_csv(json_dir, output_csv, input_length, output_length, i, p)
    print(f"Save the csv result to: {output_csv}")
    parse_csv_to_xlsx(output_csv, output_xlsx)


if __name__ == "__main__":
    runner(obj={})
