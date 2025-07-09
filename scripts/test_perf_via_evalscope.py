"""
通过 evalscope 跑 perf 测试
"""

import click

from evalscope.perf.main import run_perf_benchmark
from evalscope.perf.arguments import Arguments


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
def runner(
    ip, port, parallel, number, model, api_key, input_length, output_length, tokenizer_path, seed, loop, name, debug
):
    for i in range(0, int(loop)):
        print(f" loop {i} ".center(100, "*"))
        task_cfg = Arguments(
            parallel=[int(p) for p in parallel.split()],
            number=[int(n) for n in number.split()],
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
        print(task_cfg)

        run_perf_benchmark(task_cfg)


if __name__ == "__main__":
    runner(obj={})
