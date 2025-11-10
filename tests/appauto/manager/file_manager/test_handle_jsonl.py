import pytest
from appauto.manager.file_manager import JsonlHandler
from appauto.manager.config_manager import LoggingConfig

logger = LoggingConfig.get_logger()


jsonl_path = "tests/appauto/manager/file_manager/humaneval_sample_file.jsonl_results.jsonl"


@pytest.mark.ci
class TestHandleJsonl:
    def test_load_jsonl(self):
        jsonl = JsonlHandler(jsonl_path)
        logger.info(jsonl.data)
        assert isinstance(jsonl.data, list)

        for inner_dict in jsonl.data:
            assert isinstance(inner_dict, dict)

            logger.info(inner_dict)
            logger.info(inner_dict.result)
            logger.info(inner_dict.passed)

            assert inner_dict.result == "passed"
            assert inner_dict.passed is True
