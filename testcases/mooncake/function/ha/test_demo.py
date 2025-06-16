from appauto.manager.config_manager.config_logging import LoggingConfig

logger = LoggingConfig.get_logger()

from testcases.mooncake.function.ha.gen_data import mooncake


class TestMoonCakeDemo:
    def test_mooncake_start_client(self):
        mooncake.get()
        mooncake.put(a="b")
        assert mooncake.get("a") == "b"

    def test_2_client_1_master(self):
        if mooncake.has_server():
            ...
        mooncake.start_server()
