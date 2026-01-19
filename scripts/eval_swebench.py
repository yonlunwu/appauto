import click
from evalscope import TaskConfig, run_task


@click.command()
@click.option("--model", default="DeepSeek-V3.2", type=str, show_default=True, help="模型名称或路径")
@click.option("--ip", default="127.0.0.1", type=str, show_default=True, help="API服务的IP地址")
@click.option("--port", default=35000, type=int, show_default=True, help="API服务的端口号")
@click.option("--temperature", default=1.0, type=float, show_default=True, help="模型生成的温度系数（控制随机性）")
@click.option("--limit", default=100, type=int, show_default=True, help="评测任务的数量限制")
@click.option("--retry", default=50, type=int, show_default=True, help="模型调用失败后的重试次数")
def run_eval_task(model: str, ip: str, port: int, temperature: float, limit: int, retry: int):
    """
    基于evalscope的模型评测命令行工具，支持自定义核心运行参数
    """
    # 拼接完整的api_url（由命令行传入的ip和port组成）
    api_url = f"http://{ip}:{port}/v1"

    # 构建任务配置（将命令行参数注入配置中）
    task_cfg = TaskConfig(
        model=model,
        api_url=api_url,  # 动态拼接的API地址
        api_key="EMPTY",
        eval_type="openai_api",  # 使用API模型服务
        datasets=["swe_bench_verified"],  # 选择评测数据集
        dataset_args={
            "swe_bench_verified": {
                "extra_params": {
                    "build_docker_images": True,  # 是否构建评测所需的Docker镜像
                    "pull_remote_images_if_available": True,  # 是否拉取远程可用镜像
                    "inference_dataset_id": "princeton-nlp/SWE-bench_oracle",  # 推理数据集
                }
            }
        },
        eval_batch_size=3,
        judge_worker_num=3,  # 并行评测任务的工作线程数
        limit=limit,  # 命令行传入的数量限制
        generation_config={
            "temperature": temperature,  # 命令行传入的温度系数
            "retries": retry,  # 命令行传入的重试次数
            "chat_template_kwargs": {"thinking": True},
            "extra_body": {"chat_template_kwargs": {"thinking": True}},
        },
    )

    # 执行评测任务
    click.echo(f"开始执行评测任务，API地址：{api_url}，评测数量：{limit}")
    run_task(task_cfg=task_cfg)
    click.echo("评测任务执行完成！")


if __name__ == "__main__":
    run_eval_task()
