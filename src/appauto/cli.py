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


@cli.command(
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True, help_option_names=["-h", "--help"])
)
@click.argument("mode", type=click.Choice(["pytest", "ui"]))
@click.option("--testpaths", required=True, help="Test paths (comma-separated)")
@click.option("--testclasses", help="test class")
@click.option("--testcases", help="Python functions pattern")
# TODO 使用正确的 group & user
@click.option("--notify-group", default=None, help="Notify Group Chat ID")
@click.option("--notify-user", default="ou_de15ea583c7731052a0ab3bd370fc113", help="Notify User ID")
@click.option("--interval", default=0, help="Delay in seconds between test cases. (Default: 0)")
@click.option("--repeat", default=1, help="Delay in seconds between test cases. (Default: 0)")
@click.option("--loglevel", default="INFO", help="Log Level")
@click.option("--no-report", is_flag=True, help="Don't generate allure report (Default: False)")
@click.option("--keyword", default=None, help="Keyword (Default: None)")
@click.option("--collect-only", is_flag=True, help="Collect only test cases without executing (Default: False)")
@click.pass_context
def run(
    ctx,
    mode,
    testpaths,
    testclasses,
    testcases,
    loglevel,
    notify_group,
    notify_user,
    interval,
    repeat,
    no_report,
    keyword,
    collect_only,
):
    if collect_only:
        no_report = True
        notify_group = None
        notify_user = None

    """运行测试(pytest / ui)"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 配置日志
    LoggingConfig.config_logging(log_level=loglevel, timestamp=timestamp)
    logger = LoggingConfig.get_logger()
    logger.info(f"Starting test run at {timestamp}")

    # 解析额外参数
    extra_args = parse_extra_args(ctx.args)
    logger.debug(f"Extra args: {extra_args}")

    # 配置测试数据
    TestDataConfig().config_testdata(
        mode=mode, testpaths=testpaths, loglevel=loglevel, timestamp=timestamp, **extra_args
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
            log_level=loglevel,
            no_report=no_report,
            collect_only=collect_only,
        ).config_pytest_ini()

        # 运行 pytest
        runner = PytestRunner(
            timestamp, loglevel, notify_group, notify_user, repeat, interval, no_report, testpaths, keyword=keyword
        )
        return_code = runner.run()
        if return_code != 0:
            raise click.ClickException(f"Tests failed with return code {return_code}")
    elif mode == "ui":
        ui_runner.run(testpaths, extra_args)
    else:
        logger.error("Unsupported test type.")


def parse_extra_args(args: List[str]) -> Dict[str, str | bool]:
    """解析额外参数
    支持以下格式：
    - --key=value
    - --flag (会被解析为 --flag=true)
    """
    return {arg.lstrip("-").split("=", 1)[0]: arg.split("=", 1)[1] if "=" in arg else "true" for arg in args or []}


if __name__ == "__main__":
    cli()
