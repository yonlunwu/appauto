import pandas as pd

markdown_table = """
┏━━━━━━┳━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┓
┃      ┃      ┃      Avg ┃      P99 ┃    Gen. ┃      Avg ┃     P99 ┃      Avg ┃     P99 ┃   Success┃
┃Conc. ┃  RPS ┃  Lat.(s) ┃  Lat.(s) ┃  toks/s ┃  TTFT(s) ┃ TTFT(s) ┃  TPOT(s) ┃ TPOT(s) ┃      Rate┃
┡━━━━━━╇━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━┩
│    1 │ 0.13 │    7.551 │    7.551 │   33.90 │    1.100 │   1.100 │    0.025 │   0.025 │    100.0%│
│    5 │ 0.45 │   11.128 │   11.150 │  114.80 │    0.922 │   1.077 │    0.044 │   0.041 │    100.0%│
│   10 │ 0.63 │   15.779 │   15.819 │  161.84 │    1.021 │   1.228 │    0.066 │   0.060 │    100.0%│
│   15 │ 0.97 │   15.511 │   15.544 │  247.08 │    0.644 │   0.678 │    0.064 │   0.059 │    100.0%│
│   20 │ 0.97 │   20.650 │   20.676 │  247.63 │    0.605 │   0.635 │    0.080 │   0.079 │    100.0%│
│   25 │ 0.87 │   28.761 │   28.786 │  222.34 │    3.253 │   3.363 │    0.103 │   0.109 │    100.0%│
│   30 │ 0.99 │   30.137 │   30.172 │  254.55 │    3.196 │   3.482 │    0.120 │   0.114 │    100.0%│
│   35 │ 0.99 │   35.306 │   35.364 │  253.38 │    3.574 │   4.196 │    0.134 │   0.135 │    100.0%│
│   40 │ 1.06 │   37.530 │   37.642 │  272.02 │    4.125 │   4.843 │    0.157 │   0.140 │    100.0%│
│   45 │ 1.01 │   44.404 │   44.463 │  259.09 │    4.458 │   5.445 │    0.162 │   0.168 │    100.0%│
│   50 │ 1.08 │   46.286 │   46.354 │  276.12 │    5.084 │   5.907 │    0.176 │   0.177 │    100.0%│
└──────┴──────┴──────────┴──────────┴─────────┴──────────┴─────────┴──────────┴─────────┴──────────┘
"""

# 预处理Markdown表格
lines = [line.strip() for line in markdown_table.split("\n") if line.strip()]
lines = [line for line in lines if not line.startswith("┏") and not line.startswith("┡") and not line.startswith("└")]

# 手动定义表头（因为自动提取有问题）
headers = [
    "Conc.",
    "RPS",
    "Avg Lat.(s)",
    "P99 Lat.(s)",
    "Gen. toks/s",
    "Avg TTFT(s)",
    "P99 TTFT(s)",
    "Avg TPOT(s)",
    "P99 TPOT(s)",
    "Success Rate",
]

# 处理数据行
data = []
for line in lines[2:]:  # 跳过前两行表头
    # 分割行并清理数据
    parts = [part.strip() for part in line.split("│")]
    # 去掉首尾空元素（Markdown表格符号）
    if len(parts) > 2:
        data.append(parts[1:-1])

# 创建DataFrame
df = pd.DataFrame(data, columns=headers)

# 保存为CSV
csv_output = df.to_csv(index=False)
print(csv_output)

# 或者直接保存到文件
df.to_csv("performance_metrics.csv", index=False)
print("\nCSV文件已保存为 'performance_metrics.csv'")
