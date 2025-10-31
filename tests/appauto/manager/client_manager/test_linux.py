from appauto.manager.client_manager import BaseLinux
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()

linux = BaseLinux("192.168.110.4", "qujing", "zkyd@12#$")


class TestBaseLinux:
    def test_grep_pid(self):
        pids = linux.grep_pid("sglang.launch_server")
        logger.info(pids)
        assert pids

    def test_stop_process_by_keyword(self):
        linux.stop_process_by_keyword("sglang.launch_server", force=True)

    def test_conda_env_list(self):
        lts = linux.conda_env_list(conda_path="/home/zkyd/miniconda3/bin/conda")
        logger.info(lts)
        # assert lts

    def test_download_file(self):
        remote_path = "/home/zkyd/yanlong/yanlong_eval_file_73.jsonl_results.jsonl"
        local_path = "./yanlong_eval_file_73.jsonl_results.jsonl"
        linux.download(remote_path, local_path)

    def test_upload_file(self):
        local_path = "test_playwright.py"
        remote_path = "test_playwright.py"
        linux.upload(remote_path, local_path)

    def test_grant_directory_permission(self):
        import os

        dir_path = os.path.dirname("/mnt/data/deploy/ft-docker-compose_v3.3.0-test5.yaml")
        linux._grant_dir_permission(dir_path)
