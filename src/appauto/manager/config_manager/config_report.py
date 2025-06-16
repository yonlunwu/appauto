import os
from typing import Dict
from .config_logging import LoggingConfig

logger = LoggingConfig.get_logger()


class AllureReport(object):
    def __init__(self, test_env: Dict = None, test_summary: Dict = None, link: str = None):
        self.test_env = test_env
        self.test_summary = test_summary
        self.link = link

    def gen_allure_report(self, folder, allure_tmp_folder_time_stamp):
        folder = folder.rstrip("/") if folder.endswith("/") else folder
        logger.info(f"folder: {folder}")

        report_dir = f"reports/allure-report/{folder}/{allure_tmp_folder_time_stamp}"

        tmp_folder = f"reports/tmp/{allure_tmp_folder_time_stamp}"
        cmd = f"mv environment.properties.{allure_tmp_folder_time_stamp} {tmp_folder}/environment.properties"
        os.system(cmd)

        cmd = f"allure generate {tmp_folder} -o {report_dir} --clean"
        os.system(cmd)

        # os.system(f"rm -rf {tmp_folder}") # TODO 考虑是否需要立即删除临时路径。（后续 jenkins 中 allure 报告）
        logger.info(f"Report successfully generated to {report_dir}")

        return f"{folder}/{allure_tmp_folder_time_stamp}"
