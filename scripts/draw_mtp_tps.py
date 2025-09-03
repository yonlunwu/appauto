#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import re
from typing import List, Tuple, Dict
import sys
import matplotlib.pyplot as plt


BLOCK_START_PAT = re.compile(r"^=+ Serving Benchmark Result =+")
BLOCK_END_PAT = re.compile(r"^=+$")

RE_REQS = re.compile(r"Successful requests:\s+(\d+)")
RE_MEAN = re.compile(r"Mean ITL\s*\(ms\):\s*([0-9.]+)")
RE_MEDIAN = re.compile(r"Median ITL\s*\(ms\):\s*([0-9.]+)")


def parse_file(path: str) -> List[Dict[str, float]]:
    """
    解析日志文件，按每个“Serving Benchmark Result”块提取：
      - x: Successful requests
      - mean: Mean ITL (ms)
      - median: Median ITL (ms)
    返回块字典列表。
    """
    results = []
    curr = None

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.rstrip("\n")

                if BLOCK_START_PAT.search(line):
                    # 新块开始
                    curr = {"x": None, "mean": None, "median": None}
                    continue

                if curr is not None:
                    # 在块内解析各字段
                    m = RE_REQS.search(line)
                    if m:
                        curr["x"] = int(m.group(1))
                        continue

                    m = RE_MEAN.search(line)
                    if m:
                        curr["mean"] = float(m.group(1))
                        continue

                    m = RE_MEDIAN.search(line)
                    if m:
                        curr["median"] = float(m.group(1))
                        continue

                    # 块结束（常见是全等号行）
                    if BLOCK_END_PAT.match(line):
                        # 收尾并存入
                        results.append(curr)
                        curr = None

        # 如果文件末尾没有等号收尾，也把最后一个块塞进去
        if curr is not None:
            results.append(curr)

    except FileNotFoundError:
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        sys.exit(1)

    return results


def pick_xy(blocks: List[Dict[str, float]], metric: str) -> Tuple[List[int], List[float], int]:
    """
    从块列表中抽取 (x, y)。优先用 metric（mean/median），
    如果该块缺失此 metric，会回退到另一个指标并计数。
    返回：xs, ys, fallback_count
    """
    xs, ys = [], []
    fallback = 0
    print(f"blocks: {blocks}")
    for b in blocks:
        x = b.get("x")
        print(f"x: {x}")
        y = None
        if metric == "mean":
            y = 1 / (b.get("mean") / 1000)
            print(f"y: {y}")
            if y is None and b.get("median") is not None:
                # y = b["median"]
                y = 1 / (b["median"] / 1000)
                fallback += 1
        else:  # metric == "median"
            y = 1 / (b.get("median") / 1000)
            if y is None and b.get("mean") is not None:
                # y = b["mean"]
                y = 1 / (b["mean"] / 1000)
                fallback += 1

        if x is not None and y is not None:
            xs.append(x)
            ys.append(y)

    # 按 X 排序
    xy = sorted(zip(xs, ys), key=lambda t: t[0])
    if xy:
        xs, ys = map(list, zip(*xy))
    else:
        xs, ys = [], []

    return xs, ys, fallback


def main():
    ap = argparse.ArgumentParser(
        description="从 sglang 基准日志中提取 Successful requests 与 ITL（Mean/Median）并作图（两条折线：禁用/启用 MTP）"
    )
    ap.add_argument("--disable_mtp", help="禁用 MTP 的日志文件路径（如：4090_1gpu_1experts_disable_mtp.txt）")
    ap.add_argument("--enable_mtp", help="启用 MTP 的日志文件路径（如：4090_1gpu_1experts_enable_mtp.txt）")
    ap.add_argument(
        "--metric",
        choices=["mean", "median"],
        default="mean",
        help="纵轴选用的指标（默认 mean）。若该块缺失会自动回退到另一项。",
    )
    ap.add_argument("--output", help="保存到文件（如 output.png）。不指定则直接显示窗口。")
    args = ap.parse_args()

    # 解析两个文件
    blocks_dis = parse_file(args.disable_mtp)
    blocks_en = parse_file(args.enable_mtp)

    xs_dis, ys_dis, fb_dis = pick_xy(blocks_dis, args.metric)
    xs_en, ys_en, fb_en = pick_xy(blocks_en, args.metric)

    if not xs_dis and not xs_en:
        print("[ERROR] 未在两份日志中解析到任何数据。请检查格式或正则。", file=sys.stderr)
        sys.exit(2)

    # 绘图
    plt.figure(figsize=(9, 5))
    if xs_dis:
        plt.plot(xs_dis, ys_dis, marker="o", label="Disable MTP")
    if xs_en:
        plt.plot(xs_en, ys_en, marker="o", label="Enable MTP")

    # ylabel = "Mean ITL (ms)" if args.metric == "mean" else "Median ITL (ms)"
    ylabel = "Mean TPS" if args.metric == "mean" else "Median TPS"
    plt.xlabel("Successful requests(Concurrency)")
    plt.ylabel(ylabel)
    plt.title(f"enable mtp vs disable mtp ({ylabel})")
    # 横轴使用所有 x 值
    plt.xticks(xs_dis + xs_en)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend()
    plt.tight_layout()

    # 回退提示
    notes = []
    if fb_dis > 0:
        notes.append(f"Disable MTP有{fb_dis}处从{args.metric}回退")
    if fb_en > 0:
        notes.append(f"Enable MTP有{fb_en}处从{args.metric}回退")
    if notes:
        print("[INFO] " + "；".join(notes))

    if args.output:
        plt.savefig(args.output, dpi=150)
        print(f"[OK] 图像已保存到: {args.output}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
