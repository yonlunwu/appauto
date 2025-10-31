import pytest
from pytest import TerminalReporter

from time import time
from appauto.manager.utils_manager.format_output import format_time

from appauto.manager.notify_manager import LarkClient
from appauto.manager.config_manager import LoggingConfig, AllureReport
from appauto.manager.utils_manager.network_utils import NetworkUtils
from time import sleep

logger = LoggingConfig.get_logger()


def pytest_addoption(parser):
    parser.addoption("--timestamp", action="store", help="timestamp, used for log file and report file")
    parser.addoption("--no_report", action="store", default=False, help="Don't generate report (Default: False)")
    # TODO group_chat_id
    parser.addoption("--notify_group", action="store", default=None, help="Group Chat ID")
    parser.addoption("--notify_user", action="store", default=None, help="User Open ID")
    parser.addoption("--testpaths", action="store", help="Test paths (comma-separated)")
    parser.addoption("--preserve_the_scene", action="store_true", help="Preserve the scene after test execution")
    parser.addoption("--report_server", action="store", help="Allure report server ip")
    parser.addoption("--report_url", action="store", help="Allure report url")
    parser.addoption("--filling_report_url", action="store", help="Filling Allure report server ip")
    parser.addoption("--set_report_url_suffix", action="store", default=False, help="Set Allure report url suffix")
    parser.addoption("--interval", action="store", default=0, help="Delay in seconds between test cases")
    parser.addoption("--topic", action="store", default=None, help="The test topic")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    delay = float(item.config.getoption("--interval", default=0))
    logger.info(f"Run test start: {item.nodeid}")

    yield
    logger.info(f"Run test end: {item.nodeid}")
    result = nextitem
    logger.info(f"Next test case: {result}")

    if delay > 0:
        if nextitem is not None:
            sleep(delay)


def gen_report_and_send_lark(
    config,
    case_dict,
    report_server: str = None,
    filling_url: str = None,
    set_url_suffix: bool = False,
    topic: str = None,
):
    timestamp = config.getoption("--timestamp")
    no_report = config.getoption("--no_report")
    group_chat_id = config.getoption("--notify_group")
    user_open_id = config.getoption("--notify_user")
    testpaths = config.getoption("--testpaths")
    report_url = config.getoption("--report_url")

    lark = LarkClient()

    if no_report is True or isinstance(no_report, str) and no_report.lower() == "true":
        test_report = None

    else:
        testpaths = testpaths.replace(".py", "")

        allure = AllureReport()
        if not report_url:
            report_url = allure.gen_allure_report(testpaths, timestamp)
            report_url = str(filling_url) + "/" + report_url if filling_url else report_url
            report_url = report_url + "/index.html" if set_url_suffix else report_url
        # report_server = report_server or NetworkUtils.get_local_ip()
        report_server = report_server or f"{NetworkUtils.get_local_ip()}:8000/reports/allure-results"
        test_report = f"http://{report_server}/{report_url}"

    logger.info(f"test_report: {test_report}")

    if group_chat_id and group_chat_id.lower() != "none":
        lark.send_msg(
            lark.construct_msg_payload(group_chat_id, case_dict, env_summary=None, link=test_report, topic=topic),
            "group",
        )

    elif user_open_id and user_open_id.lower() != "none":
        lark.send_msg(
            lark.construct_msg_payload(user_open_id, case_dict, env_summary=None, link=test_report, topic=topic), "dm"
        )


def pytest_configure(config):
    config.test_start_time = time()


def pytest_terminal_summary(terminalreporter: TerminalReporter, exitstatus, config):
    """统计用例执行结果"""
    case_dict = {}

    case_dict["PASSED"] = len(terminalreporter.stats.get("passed", []))
    failed = len(terminalreporter.stats.get("failed", []))
    error = len(terminalreporter.stats.get("error", []))
    case_dict["FAILED"] = failed + error
    case_dict["SKIP"] = len(terminalreporter.stats.get("skipped", []))
    case_dict["XFAIL"] = len(terminalreporter.stats.get("xfailed", []))
    case_dict["XPASS"] = len(terminalreporter.stats.get("xpassed", []))
    case_dict["RERUN"] = len(terminalreporter.stats.get("rerun", []))

    if start_time := getattr(config, "test_start_time", None):
        run_time_s = round(time() - start_time, 2)
        case_dict["RUN_TIME"] = format_time(run_time_s)
    else:
        case_dict["RUN_TIME"] = "N/A"

    logger.info(case_dict)

    report_server = config.getoption("--report_server", None)
    # filling_url = config.getoption("--filling_report_url")
    # set_url_suffix = config.getoption("--set_report_url_suffix")
    # gen_report_and_send_lark(
    #     config, case_dict, report_server, filling_url, set_url_suffix)

    topic = config.getoption("--topic", None)

    gen_report_and_send_lark(config, case_dict, report_server, topic=topic)
