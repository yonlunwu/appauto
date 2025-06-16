import pytest
from appauto.manager.config_manager.config_logging import LoggingConfig
from time import sleep

logger = LoggingConfig.get_logger()


@pytest.mark.parametrize("x, y, z", [(1, 2, 3), (2, 3, 4)])
def test_api_demo(x, y, z):
    logger.info(f"x: {x}")
    logger.debug(f"y: {y}")
    logger.debug(f"z: {z}")
    sleep(2)
    assert x + y == z


@pytest.mark.smoke
def test_smoke():
    logger.debug("smoke test")
    assert True
