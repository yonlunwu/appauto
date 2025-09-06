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
from typing import Dict, Iterator, List

from evalscope.perf.main import run_perf_benchmark
from evalscope.perf.arguments import Arguments


from evalscope.perf.plugin.registry import register_dataset
from evalscope.perf.plugin.datasets.base import DatasetPluginBase


@register_dataset("custom")
class CustomDatasetPlugin(DatasetPluginBase):
    """读取数据集并返回 prompt。"""

    def __init__(self, query_parameters: Arguments):
        super().__init__(query_parameters)

    def build_messages(self) -> Iterator[List[Dict]]:
        """构建消息列表。"""
        for item in self.dataset_line_by_line(self.query_parameters.dataset_path):
            prompt = item.strip()
            if (
                len(prompt) > self.query_parameters.min_prompt_length
                and len(prompt) < self.query_parameters.max_prompt_length
            ):
                if self.query_parameters.apply_chat_template:
                    yield [{"role": "user", "content": prompt}]
                else:
                    yield prompt


def extract_json_to_csv(input_dir, output_csv, input_length, output_length, loop):
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
            concurrency = "1"  # 默认值

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
@click.option("--ip", default="127.0.0.1", show_default=True, help="AMaaS 管理 IP")
@click.option("--port", type=str, default=10011, show_default=True)
@click.option("--parallel", type=str, default="1 4", show_default=True, help="并发数, 请用引号引起来, 如 '1 4'")
@click.option("--number", type=str, default="1 4", show_default=True, help="请求数, 请用引号引起来, 如 '1 4'")
@click.option("--model", type=str, default="DeepSeek-R1", show_default=True, help="模型名称")
@click.option(
    "--api-key",
    type=str,
    default="AMES_205ff248c351177a_b206a9791eb618b3a7f109d9cec346a2",
    show_default=True,
    help="API Key, 从 AMaaS 上创建.",
)
# TODO input 和 output length 动态获取？
@click.option("--loop", type=int, default=1, show_default=True)
@click.option("--name", type=str, default="appauto-bench", show_default=True, help="任务名称")
@click.option("--debug", is_flag=True, show_default=True)
@click.option(
    "--dataset-path",
    type=str,
    default="custom_dataset.txt",
    show_default=True,
    help="输出 csv 文件名称, 不填写会默认填充",
)
@click.option("--output-csv", type=str, default=None, show_default=True, help="输出 csv 文件名称, 不填写会默认填充")
@click.option("--output-xlsx", type=str, default=None, show_default=True, help="同时输出一份 xlsx 文件")
def runner(
    ip,
    port,
    parallel,
    number,
    model,
    api_key,
    loop,
    name,
    debug,
    dataset_path,
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
            dataset="custom",
            dataset_path=dataset_path,
            extra_args={"ignore_eos": True},
            name=f"{name}-{i}",
            debug=debug,
            max_tokens=512,
            min_tokens=512,
            # 如果是自定义数据集，就不能指定输入长度相关参数
            # max_prompt_length=512,
            # min_prompt_length=512,
            stream=True
        )

        run_perf_benchmark(task_cfg)

        # 从 json 提取至 csv
        if len(number) == 1:
            json_dir = task_cfg.outputs_dir
            extract_json_to_csv(json_dir, output_csv, input_length="custom", output_length="custom", loop=i)

        elif len(number) > 1:
            json_dir = "/".join(task_cfg.outputs_dir.split("/")[:-2])
            extract_json_to_csv(json_dir, output_csv, input_length="custom", output_length="custom", loop=i)

    print(f"Save the csv result to: {output_csv}")

    parse_csv_to_xlsx(output_csv, output_xlsx)


if __name__ == "__main__":
    runner(obj={})
