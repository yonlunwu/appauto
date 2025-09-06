"""
基于 evalscope + VLMEvalKit 评测 vlm 精度, 参考:
https://evalscope.readthedocs.io/zh-cn/latest/user_guides/backend/vlmevalkit_backend.html#id6
"""

import sys
import click
import subprocess
from evalscope.run import run_task
from evalscope.config import TaskConfig


def get_ft_port() -> int | None:
    try:
        cmd = "pgrep -f 'ftransformers.launch_server' -a | grep -o 'port [0-9]*' | awk '{print $2}'"
        result = subprocess.check_output(cmd, shell=True, text=True).strip()
        return int(result) if result.isdigit() else None
    except (subprocess.CalledProcessError, ValueError):
        return None


@click.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True, help_option_names=["-h", "--help"])
)
@click.option(
    "--ip", type=str, default="127.0.0.1", show_default=True, help="Set to 127.0.0.1 to avoid network issues."
)
@click.option(
    "--port",
    type=int,
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
    default="aime24",
    show_default=True,
    help="Dataset names, enclosed in quotes, e.g., 'aime24'",
)
@click.option(
    "--dataset-args",
    type=str,
    default=None,
    show_default=True,
    help=('Dataset arguments, JSON string, e.g., \'{"aime24": {"prompt_template": "..."} }\''),
)
@click.option(
    "--limit", type=int, default=None, show_default=True, help="Control evaluation scope: first n questions per subset"
)
@click.option("--concurrency", type=int, default=16, show_default=True, help="Evaluation concurrency")
@click.option("--max-tokens", type=int, default=None, show_default=True, help="Maximum tokens for input + output")
def runner(
    ip,
    port,
    model,
    api_key,
    datasets,
    limit,
    concurrency,
    max_tokens,
    dataset_args,
):
    port = port or get_ft_port()
    if not port:
        print("Failed to get ftransformers port. Please check and rerun, or pass it via --port.")
        return
    print("Starting evaluation task...")
    print(f"Command-line arguments: {sys.argv}")

    generation_config = {
        "do_sample": True,
        "temperature": 0.6,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    if max_tokens:
        generation_config["max_tokens"] = int(max_tokens)

    datasets_list = datasets.strip().split()
    task_cfg = TaskConfig(
        eval_backend="VLMEvalKit",
        eval_config={
            "model": [
                {
                    "type": model,
                    "name": "CustomAPIModel",
                    "api_base": f"http://{ip}:{port}/v1/chat/completions",
                    "key": api_key or "EMPTY",
                    "temperature": 0.6,
                    "img_size": -1,
                    "max_tokens": max_tokens,
                    "video_llm": False,
                }
            ],
            "data": datasets_list,
            "limit": limit,
            "mode": "all",
            "reuse": False,
            "nproc": concurrency,
            "judge": "exact_matching",
            # "verbose": True,
            # "debug": True
        },
    )

    if limit and isinstance(limit, int):
        task_cfg.limit = limit

    if dataset_args:
        task_cfg.dataset_args = eval(dataset_args)

    try:
        run_task(task_cfg=task_cfg)
        print("Evaluation task completed")
    except Exception as e:
        print(f"Task execution error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    runner(obj={})
