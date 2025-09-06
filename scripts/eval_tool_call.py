"""
# 评测Qwen3-Coder模型工具调用能力("bfcl_v3")
https://evalscope.readthedocs.io/zh-cn/latest/best_practice/qwen3_coder.html
https://evalscope.readthedocs.io/zh-cn/latest/third_party/bfcl_v3.html
https://evalscope.readthedocs.io/zh-cn/latest/third_party/tau_bench.html
"""

import sys
import click
import subprocess
from typing import Literal
from evalscope.run import run_task
from evalscope.config import TaskConfig


def get_ft_port() -> int | None:
    try:
        cmd = "pgrep -f 'ftransformers.launch_server' -a | grep -o 'port [0-9]*' | awk '{print $2}'"
        result = subprocess.check_output(cmd, shell=True, text=True).strip()
        return int(result) if result.isdigit() else None
    except (subprocess.CalledProcessError, ValueError):
        return None


def construct_dataset_args(model, datasets: Literal["bfcl_v3", "tau_bench"], api_key, ip, port, max_tokens):
    assert datasets in ["bfcl_v3", "tau_bench"]

    if datasets == "bfcl_v3":
        dataset_args = {
            "bfcl_v3": {
                "extra_params": {
                    # 模型在函数名称中拒绝使用点号（`.`）；设置此项，以便在评估期间自动将点号转换为下划线。
                    "underscore_to_dot": True,
                    # 模型是否为函数调用模型（Function Calling Model），如果是则会启用函数调用相关的配置；否则会使用prompt绕过函数调用。
                    "is_fc_model": True,
                }
            }
        }

    elif datasets == "tau_bench":
        dataset_args = {
            "tau_bench": {
                "subset_list": ["airline", "retail"],  # 选择评测领域
                "extra_params": {
                    "user_model": model,
                    "api_key": api_key,
                    "api_base": f"http://{ip}:{port}/v1/",
                    "generation_config": {"temperature": 0.7, "max_tokens": max_tokens},
                },
            }
        }

    return dataset_args


def construct_generation_config(model, datasets: Literal["bfcl_v3", "tau_bench"], max_tokens: int = None):

    assert datasets in ["bfcl_v3", "tau_bench"]

    if datasets == "bfcl_v3":
        if model == "Qwen3-Coder-480B-A35B-Instruct-GPU-weight":
            generation_config = {
                "temperature": 0,
                "max_tokens": 32000,
                "parallel_tool_calls": True,  # 启用并行函数调用
            }

        else:
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 20,
                "repetition_penalty": 1.05,
                "parallel_tool_calls": True,  # 启用并行函数调用
            }

    elif datasets == "tau_bench":

        generation_config = {"temperature": 0.6, "n": 1}

    if max_tokens:
        generation_config["max_tokens"] = max_tokens  # 设置最大生成长度

    return generation_config


@click.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True, help_option_names=["-h", "--help"])
)
@click.option(
    "--ip", type=str, default="127.0.0.1", show_default=True, help="Set to 127.0.0.1 to avoid network issues."
)
@click.option(
    "--port",
    type=str,
    default=None,
    show_default=True,
    help="ftransformers port, will be auto-detected if not provided.",
)
@click.option("--model", type=str, default="DeepSeek-R1", show_default=True, help="Model name")
@click.option(
    "--api-key",
    type=str,
    default="AMES_ec2640eb92c6cbed_bea2b0c8abfb8885b870586a72761e61",
    show_default=True,
    help="API Key, created from AMaaS.",
)
@click.option(
    "--datasets",
    type=str,
    default="bfcl_v3",
    show_default=True,
    help="Dataset names, enclosed in quotes, e.g., 'bfcl_v3'",
)
@click.option(
    "--limit", type=int, default=None, show_default=True, help="Control evaluation scope: first n questions per subset"
)
@click.option("--concurrency", type=int, default=8, show_default=True, help="Evaluation concurrency")
@click.option("--timeout", type=int, default=6000, show_default=True, help="Timeout duration, unit: seconds")
@click.option("--max-tokens", type=int, default=32000, show_default=True, help="Maximum tokens for input + output")
@click.option("--disable-debug", is_flag=True, show_default=True, help="Disable debug mode")
def runner(
    ip,
    port,
    model,
    api_key,
    datasets,
    limit,
    disable_debug,
    timeout,
    concurrency,
    max_tokens,
):
    port = port or get_ft_port()

    if not port:
        print("Failed to get ftransformers port. Please check and rerun, or pass it via --port.")
        return

    print("Starting evaluation task...")

    print(f"Command-line arguments: {sys.argv}")

    dataset_args = construct_dataset_args(model, datasets, api_key, ip, port, max_tokens)

    generation_config = construct_generation_config(model, datasets, max_tokens)

    task_cfg = TaskConfig(
        model=model,
        api_url=f"http://{ip}:{port}/v1/",
        api_key=api_key,
        eval_type="openai_api",  # 使用API模型服务
        datasets=[datasets],
        eval_batch_size=concurrency,
        generation_config=generation_config,
        dataset_args=dataset_args,
        ignore_errors=True,  # 忽略错误，可能会被模型拒绝的测试用例
        debug=not disable_debug,
        timeout=int(timeout),
    )

    if limit and isinstance(limit, int):
        task_cfg.limit = limit

    print(type(task_cfg.generation_config))
    print(task_cfg.generation_config)

    try:
        run_task(task_cfg=task_cfg)
        print("Evaluation task completed")
    except Exception as e:
        print(f"Task execution error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    runner(obj={})
