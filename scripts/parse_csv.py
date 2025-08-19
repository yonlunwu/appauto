"""
性能测试后会生成 csv, 需要整理 csv 为 excel
"""

import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

in_csv = "/Users/ryanyang/work/approaching/code/autotest/appauto/performance_metrics.csv"  # 原始 csv
out_xlsx = "output.xlsx"  # 带颜色的结果文件


def parse_csv_to_xlsx(input_csv, output_xlsx):
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
    print("已生成 Excel：", out_xlsx)
