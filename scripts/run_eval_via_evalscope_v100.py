"""
evalscope = v1.0.0
"""

import sys
import click
import subprocess
from evalscope.run import run_task
from evalscope.config import TaskConfig


def get_ft_port() -> int | None:
    try:
        # cmd = "ps aux | grep ftransformers.launch_server | grep -v grep | grep -o 'port [0-9]*' | awk '{print $NF}'"
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
    default="aime24",
    show_default=True,
    help="Dataset names, enclosed in quotes, e.g., 'aime24'",
)
@click.option(
    "--dataset-args",
    type=str,
    default=None,
    show_default=True,
    help=(
        'Dataset arguments, in JSON format, enclosed in quotes, e.g., \'{"aime24": '
        '{"prompt_template": "{query}\nPlease reason step by step and place your final answer within boxed{{}}. '
        "Force Requirement: 1.only the final answer should be wrapped in boxed{{}}; "
        "2.no other numbers or text should be enclosed in boxed{{}}. 3.Answer in English.\"}}'"
    ),
)
@click.option(
    "--limit", type=int, default=None, show_default=True, help="Control evaluation scope: first n questions per subset"
)
@click.option("--concurrency", type=int, default=8, show_default=True, help="Evaluation concurrency")
@click.option("--timeout", type=int, default=6000, show_default=True, help="Timeout duration, unit: seconds")
@click.option("--max-tokens", type=int, default=None, show_default=True, help="Maximum tokens for input + output")
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
    dataset_args,
):
    dataset_names = datasets.strip().split()

    port = port or get_ft_port()

    if not port:
        print("Failed to get ftransformers port. Please check and rerun, or pass it via --port.")
        return

    print("Starting evaluation task...")

    print(f"Command-line arguments: {sys.argv}")

    task_cfg = TaskConfig(
        model=model,
        datasets=dataset_names,
        debug=not disable_debug,
        stream=True,
        timeout=int(timeout),
        eval_batch_size=concurrency,
        api_url=f"http://{ip}:{port}/v1/",
        api_key=api_key,
        eval_type="openai_api",
        generation_config={
            "do_sample": True,
            "temperature": 0.6,
            "chat_template_kwargs": {"enable_thinking": False},
        },
    )

    if limit and isinstance(limit, int):
        task_cfg.limit = limit

    if dataset_args:
        task_cfg.dataset_args = eval(dataset_args)

    print(type(task_cfg.generation_config))
    print(task_cfg.generation_config)

    if max_tokens:
        task_cfg.generation_config.max_tokens = int(max_tokens)

    try:
        run_task(task_cfg=task_cfg)
        print("Evaluation task completed")
    except Exception as e:
        print(f"Task execution error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    runner(obj={})
