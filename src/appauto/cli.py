import sys
import click
from typing import Dict, List
from datetime import datetime
from pathlib import Path
from appauto import __version__
from appauto.manager.config_manager import LoggingConfig, PytestConfig, TestDataConfig
from appauto.runners.pytest_runner import PytestRunner
from appauto.runners import ui_runner


@click.group()
@click.version_option(__version__, prog_name="appauto")
def cli():
    """appauto 命令行工具"""
    pass


@cli.group()
def env():
    """环境部署命令"""
    pass


@cli.group()
def bench():
    """benchmark"""
    pass


@env.group()
def sglang():
    """管理 sglang 服务"""
    pass


@bench.group()
def evalscope():
    """通过 evalscope 跑 benchmark, 比如 eval 和 perf"""
    pass


@cli.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True, help_option_names=["-h", "--help"])
)
@click.argument("mode", type=click.Choice(["pytest", "ui"]))
@click.option("--testpaths", required=True, help="Test paths (comma-separated)")
@click.option("--testclasses", help="test class")
@click.option("--testcases", help="Python functions pattern")
@click.option("--case-level", help="Case level marker")
# TODO 使用正确的 group & user
@click.option("--notify-group", default=None, show_default=True, help="Notify Group Chat ID")
# oc_69e39d9b1f06ea42ba76ce50e68acc77: sglang 8 卡测试
# @click.option("--notify-user", default="ou_de15ea583c7731052a0ab3bd370fc113", help="Notify User ID")
@click.option("--notify-user", default=None, show_default=True, help="Notify User ID")
@click.option("--interval", default=0, show_default=True, help="Delay in seconds between test cases.")
@click.option("--repeat", default=1, show_default=True, help="Repeat test cases")
@click.option("--log-level", default="INFO", show_default=True, help="Log Level")
@click.option("--no-report", is_flag=True, show_default=True, help="Don't generate allure report")
@click.option("--keyword", default=None, show_default=True, help="Keyword")
@click.option("--collect-only", is_flag=True, show_default=True, help="Collect only test cases without executing")
@click.option("--report-server", default=None, show_default=True, help="Report Server")
@click.option("--report-url", default=None, show_default=True, help="Report URL")
@click.option("--topic", type=str, default=None, show_default=True, help="The test topic")
@click.option("--lark-user", type=str, default=None, show_default=True, help="The lark user")
@click.pass_context
def run(
    ctx,
    mode,
    testpaths,
    testclasses,
    testcases,
    case_level,
    log_level,
    notify_group,
    notify_user,
    interval,
    repeat,
    no_report,
    keyword,
    collect_only,
    report_server,
    report_url,
    topic,
    lark_user,
):
    """运行测试(pytest / ui)"""
    if collect_only:
        no_report = True
        notify_group = None
        notify_user = None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 配置日志
    LoggingConfig.config_logging(log_level=log_level, timestamp=timestamp)
    logger = LoggingConfig.get_logger()
    logger.info(f"Starting test run at {timestamp}")

    # 解析额外参数
    extra_args = parse_extra_args(ctx.args)
    logger.debug(f"Extra args: {extra_args}")

    # 配置测试数据
    TestDataConfig.cleanup()
    TestDataConfig().config_testdata(
        mode=mode, testpaths=testpaths, log_level=log_level, timestamp=timestamp, **extra_args
    )

    # 运行测试
    if mode == "pytest":
        # 配置 pytest
        test_dir = Path(testpaths)
        PytestConfig(
            timestamp,
            test_dir,
            testclasses,
            testcases,
            log_level=log_level,
            no_report=no_report,
            collect_only=collect_only,
            case_level=case_level,
        ).config_pytest_ini()

        # 运行 pytest
        runner = PytestRunner(
            timestamp,
            log_level,
            notify_group,
            notify_user,
            repeat,
            interval,
            no_report,
            testpaths,
            keyword=keyword,
            report_server=report_server,
            report_url=report_url,
            topic=topic,
            lark_user=lark_user,
        )
        return_code = runner.run()
        if return_code != 0:
            raise click.ClickException(f"Tests failed with return code {return_code}")
    elif mode == "ui":
        ui_runner.run(testpaths, extra_args)
    else:
        logger.error("Unsupported test type.")


@env.group()
def deploy():
    """通过 appauto 执行部署任务"""
    pass


@deploy.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True, help_option_names=["-h", "--help"])
)
@click.option("--ip", required=True, help="远程主机 IP")
@click.option("--user", default=None, show_default=True, help="消息卡片中的用户信息, 便于跟踪结果.")
@click.option("--ssh-user", default="qujing", required=True, show_default=True, help="SSH 用户名")
@click.option("--ssh-password", default="qujing@$#21", show_default=True, help="SSH 密码")
@click.option("--ssh-port", default=22, show_default=True, help="SSH 端口")
@click.option("--tag", required=True, show_default=True, help="目标 tag, 比如: v3.3.1")
@click.option(
    "--tar-name", required=True, show_default=True, help="tar 包名, 默认在 /mnt/data/deploy/ 下, 需要自行上传."
)
def amaas(ip, user, ssh_user, ssh_password, ssh_port, tar_name, tag):
    """在远程服务器部署 amaas"""
    from appauto.env import DeployAmaaS
    from appauto.manager.notify_manager import LarkClient

    deploy = DeployAmaaS(ip, ssh_user, ssh_password, ssh_port)
    result = deploy.deploy(tar_name, tag, force_load=True)

    result_summary = {"PASSED": "yes"} if result == "succeed" else {"FAILED": "yes"}

    lark = LarkClient()
    payload = lark.construct_msg_payload(
        "oc_23c12f5d099f09675a7d6e18d873230f",
        result_summary,
        {"ip": ip},
        topic="appauto 部署 amaas",
        report_card=False,
        user=user,
    )
    lark.send_msg(payload, "group")

    if result == "failed":
        sys.exit(1)


@deploy.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True, help_option_names=["-h", "--help"])
)
@click.option("--ip", required=True, help="远程主机 IP")
@click.option("--user", default=None, show_default=True, help="消息卡片中的用户信息, 便于跟踪结果.")
@click.option("--ssh-user", default="qujing", required=True, show_default=True, help="SSH 用户名")
@click.option("--ssh-password", default="qujing@$#21", show_default=True, help="SSH 密码")
@click.option("--ssh-port", default=22, show_default=True, help="SSH 端口")
@click.option("--image", required=True, show_default=True, help="image name, 比如: approachingai/ktransformers")
@click.option("--tag", required=True, show_default=True, help="目标 tag, 比如: 3.3.2rc1.post1")
@click.option(
    "--tar-name", required=True, show_default=True, help="tar 包名, 默认在 /mnt/data/deploy/ 下, 需要自行上传."
)
def ft(ip, user, ssh_user, ssh_password, ssh_port, tar_name, image, tag):
    """在远程服务器部署 zhiwen-ft"""
    from appauto.env import DeployFT
    from appauto.manager.notify_manager import LarkClient

    deploy = DeployFT(ip, ssh_user, ssh_password, ssh_port)
    result = deploy.deploy(tar_name, tag=tag, image=image)

    result_summary = {"PASSED": "yes"} if result == "succeed" else {"FAILED": "yes"}

    lark = LarkClient()
    payload = lark.construct_msg_payload(
        "oc_23c12f5d099f09675a7d6e18d873230f",
        result_summary,
        {"ip": ip},
        topic="appauto 部署 zhiwen-ft",
        report_card=False,
        user=user,
    )
    lark.send_msg(payload, "group")

    if result == "failed":
        sys.exit(1)


@evalscope.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True, help_option_names=["-h", "--help"])
)
@click.option("--base-ft", is_flag=True, show_default=True, help="是否基于 ft 容器跑测试")
@click.option("--base-amaas", is_flag=True, show_default=True, help="是否基于 amaas 跑测试")
@click.option("--skip-launch", is_flag=True, show_default=True, help="是否需要拉起模型(模型已经运行则无需拉起模型.)")
@click.option("--ip", default="192.168.110.15", show_default=True, help="服务器 IP")
@click.option("--port", default=10011, show_default=True, help="API 端口, 基于 AMaaS 测试时固定为 10011.")
@click.option("--ssh-user", default="zkyd", show_default=True, help="SSH 用户名")
@click.option("--ssh-password", default="zkyd@12#$", show_default=True, help="SSH 密码")
@click.option("--ssh-port", type=int, default=22, show_default=True, help="SSH 端口")
@click.option("--parallel", type=str, default="1 4", show_default=True, help="并发度")
@click.option(
    "--number",
    type=str,
    default="5 ",
    show_default=True,
    help="每个线程内部依次请求数, 比如设置为 5, 表示每个线程内部都会顺序发 5 个请求。",
)
@click.option("--model", type=str, required=True, help="模型名称, 比如: DeepSeek-R1-0528-GPU-weight")
@click.option("--tp", type=int, show_default=True, help="几卡拉起模型")
@click.option("--launch-timeout", type=int, default=900, show_default=True, help="模型拉起超时时间(S)")
@click.option(
    "--tokenizer-path",
    type=str,
    default=None,
    show_default=True,
    help="tokenizer 路径, 默认不填, 使用模型自带 tokenizer",
)
@click.option("--input-length", type=int, default=128, show_default=True, help="输入长度")
@click.option("--output-length", type=int, default=512, show_default=True, help="输出长度")
@click.option("--loop", type=int, default=1, show_default=True, help="循环次数")
@click.option("--debug", is_flag=True, show_default=True, help="是否开启 debug 模式")
@click.option("--read-timeout", type=int, default=600, show_default=True, help="读取超时时间")
@click.option("--keep-model", is_flag=True, show_default=True, help="是否保持模型拉起状态")
def perf(
    ip,
    port,
    ssh_user,
    ssh_password,
    ssh_port,
    parallel,
    number,
    model,
    tp,
    launch_timeout,
    tokenizer_path,
    input_length,
    output_length,
    read_timeout,
    loop,
    debug,
    base_ft,
    base_amaas,
    keep_model,
    skip_launch,
):
    """
    基于 evalscope 跑模型性能测试(基于 ft)
    """
    from appauto.operator.amaas_node import AMaaSNode
    from appauto.manager.error_manager.model_store import ModelCheckError, ModelRunError

    assert base_ft or base_amaas, "Either --base-ft or --base-amaas must be specified."

    if base_ft:
        ft = AMaaSNode(ip, ssh_user, ssh_password, ssh_port, skip_api=True).cli.docker_ctn_factory.ft

        try:
            if not skip_launch:
                ft.launch_model_in_thread(model, tp, "perf", port, wait_for_running=True, timeout_s=launch_timeout)

            res_xlsx = ft.run_perf_via_evalscope(
                port,
                model,
                parallel,
                number,
                input_length,
                output_length,
                read_timeout,
                loop=loop,
                debug=debug,
                tokenizer_path=tokenizer_path,
            )

            if not keep_model:
                ft.stop_model(model)

            return res_xlsx

        except (ModelCheckError, ModelRunError) as e:
            ft.stop_model(model)
            print(f" ❌ test failed: {e}")
            raise e

        except Exception as e:
            print(f" ❌ test failed: {e}")
            raise e

    elif base_amaas:
        from appauto.tool.evalscope.perf import EvalscopePerf

        amaas = AMaaSNode(ip, ssh_user, ssh_password, ssh_port)

        model_store = amaas.api.init_model_store.llm.filter(name=model)[0]

        try:
            if not skip_launch:
                amaas.api.launch_model_with_perf(tp, model_store, model, launch_timeout)

            evalscope = EvalscopePerf(
                amaas.cli,
                model,
                ip,
                10011,
                parallel,
                number,
                tokenizer_path or f"/mnt/data/models/{model}",
                amaas.api.api_keys[0].value,
                input_length,
                output_length,
                read_timeout,
                loop=loop,
                debug=debug,
            )
            evalscope.run_perf()

            if not keep_model:
                amaas.api.stop_model(model_store, "llm")

            return evalscope.output_xlsx

        except (ModelCheckError, ModelRunError) as e:
            amaas.api.stop_model(model_store, "llm")
            print(f" ❌ test failed: {e}")
            raise e

        except Exception as e:
            print(f" ❌ test failed: {e}")
            raise e


@evalscope.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True, help_option_names=["-h", "--help"])
)
@click.option("--base-ft", is_flag=True, show_default=True, help="是否基于 ft 容器跑测试")
@click.option("--base-amaas", is_flag=True, show_default=True, help="是否基于 amaas 跑测试")
@click.option("--skip-launch", is_flag=True, show_default=True, help="是否需要拉起模型(模型已经运行则无需拉起模型.)")
@click.option("--ip", default="192.168.110.15", show_default=True, help="服务器 IP")
@click.option("--port", default=10011, show_default=True, help="API 端口, 基于 AMaaS 测试时固定为 10011.")
@click.option("--ssh-user", default="zkyd", show_default=True, help="SSH 用户名")
@click.option("--ssh-password", default="zkyd@12#$", show_default=True, help="SSH 密码")
@click.option("--ssh-port", type=int, default=22, show_default=True, help="SSH 端口")
@click.option("--model", type=str, required=True, help="模型名称, 比如: DeepSeek-R1-0528-GPU-weight")
@click.option("--tp", type=int, show_default=True, help="几卡拉起模型")
@click.option("--launch-timeout", type=int, default=900, show_default=True, help="模型拉起超时时间(S)")
@click.option("--dataset", type=str, default="aime24", show_default=True, help="Dataset names, e.g., 'aime24'")
@click.option(
    "--dataset-args",
    type=str,
    default=None,
    show_default=True,
    help=(
        'Dataset arguments, in JSON format, enclosed in quotes, e.g., \'{"aime24": '
        '{"prompt_template": "{question}\nPlease reason step by step and place your final answer within boxed{{}}. '
        "Force Requirement: 1.only the final answer should be wrapped in boxed{{}}; "
        "2.no other numbers or text should be enclosed in boxed{{}}. 3.Answer in English.\"}}'"
    ),
)
@click.option("--max-tokens", type=int, default=None, show_default=True, help="Maximum tokens for input + output")
@click.option("--concurrency", type=int, default="2", show_default=True, help="并发度")
@click.option("--limit", type=int, default=None, show_default=True, help="限制每个子集只跑前 n 题")
@click.option("--temperature", type=float, default=0.6, show_default=True, help="温度, 默认 0.6")
@click.option("--keep-model", is_flag=True, show_default=True, help="是否保持模型拉起状态")
@click.option("--enable-thinking", is_flag=True, show_default=True, help="是否开启 thinking 模式")
@click.option("--debug", is_flag=True, show_default=True, help="是否开启 debug 模式")
def eval(
    ip,
    port,
    ssh_user,
    ssh_password,
    ssh_port,
    dataset,
    max_tokens,
    model,
    tp,
    launch_timeout,
    concurrency,
    limit,
    dataset_args,
    temperature,
    enable_thinking,
    debug,
    base_ft,
    base_amaas,
    keep_model,
    skip_launch,
):

    from appauto.operator.amaas_node import AMaaSNode
    from appauto.manager.error_manager.model_store import ModelCheckError, ModelRunError

    if base_ft:
        ft = AMaaSNode(ip, ssh_user, ssh_password, ssh_port, skip_api=True).cli.docker_ctn_factory.ft

        try:
            if not skip_launch:
                ft.launch_model_in_thread(model, tp, "perf", port, wait_for_running=True, timeout_s=launch_timeout)

            score = ft.run_eval_via_evalscope(
                port, model, dataset, max_tokens, concurrency, limit, dataset_args, temperature
            )
            print(f"eval finished. score: {score}")
            return score

        except (ModelCheckError, ModelRunError) as e:
            ft.stop_model(model)
            print(f" ❌ test failed: {e}")
            raise e

        except Exception as e:
            print(f" ❌ test failed: {e}")
            raise e

    # TODO 测试
    elif base_amaas:
        from appauto.tool.evalscope.eval import EvalscopeEval

        amaas = AMaaSNode(ip, ssh_user, ssh_password, ssh_port)

        model_store = amaas.api.init_model_store.llm.filter(name=model)[0]

        try:
            if not skip_launch:
                amaas.api.launch_model_with_default(tp, model_store, model, launch_timeout)

            evalscope = EvalscopeEval(
                amaas.cli,
                model,
                "127.0.0.1",
                port,
                dataset,
                max_tokens,
                concurrency,
                limit,
                dataset_args,
                temperature,
                enable_thinking,
                debug,
                api_key=amaas.api.api_keys[0].value,
            )

            evalscope.run_eval()
            print(f"score: {evalscope.score}")

            if not keep_model:
                amaas.api.stop_model(model_store, "llm")

            return evalscope.score

        except (ModelCheckError, ModelRunError) as e:
            amaas.api.stop_model(model_store, "llm")
            print(f" ❌ test failed: {e}")
            raise e

        except Exception as e:
            print(f" ❌ test failed: {e}")
            raise e


def parse_extra_args(args: List[str]) -> Dict[str, str | bool]:
    """解析额外参数
    支持以下格式：
    - --key=value
    - --flag (会被解析为 --flag=true)
    """
    return {arg.lstrip("-").split("=", 1)[0]: arg.split("=", 1)[1] if "=" in arg else "true" for arg in args or []}


if __name__ == "__main__":
    cli()
